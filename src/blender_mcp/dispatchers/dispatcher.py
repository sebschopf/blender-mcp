"""Dispatcher utility for registering and dispatching BlenderMCP handlers.

This module is a relocated copy of the top-level `blender_mcp.dispatcher`.
Relative imports have been adjusted so this file lives inside the
`blender_mcp.dispatchers` package.
"""
# Conflicts resolved: removed leftover merge markers from prior merge
# isort: skip_file

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional

from ..errors import (
    HandlerError as CanonicalHandlerError,
    HandlerNotFoundError as CanonicalHandlerNotFoundError,
)
from ..types import DispatcherResult
from .abc import AbstractDispatcher
from .bridge import BridgeService, call_gemini_cli, call_mcp_tool
from .command_adapter import CommandAdapter
from .compat import CommandDispatcher as _CommandDispatcherCompat
from .executor import HandlerExecutor
from .policies import PolicyChecker
from .strategies import (
    HandlerResolutionStrategy,
    DefaultHandlerResolutionStrategy,
    PolicyStrategy,
    DefaultPolicyStrategy,
)
from .strategies.instrumentation import InstrumentationStrategy  # type: ignore
from .registry import HandlerRegistry

logger = logging.getLogger(__name__)


# Backwards-compatible simple exception types used by some tests/modules
# Exceptions moved to `exceptions.py` and imported above to keep
# this module focused on dispatch logic.


Handler = Callable[[Dict[str, Any]], Any]


class Dispatcher(AbstractDispatcher):
    def __init__(
        self,
        *,
        executor_factory: Optional[Callable[[], ThreadPoolExecutor]] = None,
        policy_check: Optional[PolicyChecker] = None,
        handler_resolution_strategy: Optional[HandlerResolutionStrategy] = None,
        policy_strategy: Optional[PolicyStrategy] = None,
        instrumentation_strategy: Optional[InstrumentationStrategy] = None,
    ) -> None:
        """Create a Dispatcher.

        executor_factory: optional callable that returns a ThreadPoolExecutor
        (or context-manager compatible object). If provided, it's used by
        `dispatch_with_timeout` to create executors, allowing callers to
        inject test doubles or alternative executors.
        """
        self._registry = HandlerRegistry()
        self._executor_factory = executor_factory
        self._executor = HandlerExecutor(executor_factory)
        # optional policy checker callable wired into CommandAdapter
        self._policy_check = policy_check
        # strategies (fall back to defaults to preserve existing behavior)
        self._handler_resolution_strategy = handler_resolution_strategy or DefaultHandlerResolutionStrategy()
        self._policy_strategy = policy_strategy or DefaultPolicyStrategy()
        # optional instrumentation hook (no-op if None)
        self._instrumentation = instrumentation_strategy

    # --- Policy injection helpers ---
    def set_policy_check(self, policy_check: Optional[PolicyChecker]) -> None:
        """Set or clear the instance-level PolicyChecker.

        The `dispatch_command` method uses this policy by default. A per-call
        `policy_check` argument to `dispatch_command` will override this value.
        """
        self._policy_check = policy_check

    def get_policy_check(self) -> Optional[PolicyChecker]:
        """Return the current instance-level PolicyChecker (or None)."""
        return self._policy_check

    def register(self, name: str, fn: Handler, *, overwrite: bool = False) -> None:
        """Register a handler by name.

        By default `overwrite=False` and attempting to register an already
        existing name will raise ValueError (audit-friendly). Set
        `overwrite=True` to replace existing handlers.
        """
        self._registry.register(name, fn, overwrite=overwrite)
        logger.debug("registered handler %s (overwrite=%s)", name, overwrite)

    def unregister(self, name: str) -> None:
        """Remove a handler if present (no-op if missing)."""
        self._registry.unregister(name)
        logger.debug("unregistered handler %s", name)

    def list_handlers(self) -> List[str]:
        """Return a sorted list of registered handler names."""
        return self._registry.list_handlers()

    def _resolve_handler_or_service(self, name: str) -> Optional[Handler]:
        """Return a callable for a registered handler or wrap a service fallback.

        - If a handler is registered under `name`, return it as-is.
        - Else if a service exists in the services registry, return a thin
          wrapper that invokes the service via `_invoke_service`.
        - Else return None.
        """
        fn = self._registry.get(name)
        if fn is not None:
            return fn
        try:
            # Lazy import to avoid import cycles at module import time
            from ..services import registry as service_registry  # type: ignore
        except Exception:  # pragma: no cover - import error improbable
            return None
        if service_registry and service_registry.has_service(name):
            service = service_registry.get_service(name)

            def _wrapped(params: Dict[str, Any]) -> Any:
                return self._invoke_service(service, params)

            logger.debug("resolved service fallback for %s", name)
            return _wrapped
        return None

    def _instrument_start(self, name: str, params: Optional[Dict[str, Any]]) -> float:
        if self._instrumentation is None:
            return 0.0
        try:
            start = __import__("time").perf_counter()
            self._instrumentation.on_dispatch_start(name, (params or {}))
            return start
        except Exception:
            return 0.0

    def _instrument_success(self, name: str, result: Any, start_ts: float) -> None:
        if self._instrumentation is None:
            return
        try:
            elapsed = (__import__("time").perf_counter() - start_ts) if start_ts else 0.0
            self._instrumentation.on_dispatch_success(name, result, elapsed)
        except Exception:
            pass

    def _instrument_error(self, name: str, exc: Exception, start_ts: float) -> None:
        if self._instrumentation is None:
            return
        try:
            elapsed = (__import__("time").perf_counter() - start_ts) if start_ts else 0.0
            self._instrumentation.on_dispatch_error(name, exc, elapsed)
        except Exception:
            pass
    def dispatch(self, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Call the handler named `name` with `params` and return its result.

        If the handler is not found, returns None.
        """
        fn = self._handler_resolution_strategy.resolve(self, name)
        if fn is None:
            logger.debug("no handler for %s", name)
            return None
        logger.debug("dispatching %s with params=%s", name, params)
        start_ts = self._instrument_start(name, params)
        try:
            result = fn(params or {})
            self._instrument_success(name, result, start_ts)
            return result
        except Exception as exc:
            # wrap in HandlerError for compatibility with code that expects
            # handler exceptions to be wrapped
            logger.exception("handler %s raised", name)
            self._instrument_error(name, exc, start_ts)
            raise CanonicalHandlerError(name, exc) from exc

    def dispatch_strict(self, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Like `dispatch` but raises KeyError if the handler is missing."""
        fn = self._handler_resolution_strategy.resolve(self, name)
        if fn is None:
            raise KeyError(name)
        return self.dispatch(name, params)

    def dispatch_with_timeout(self, name: str, params: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> Any:
        """Call handler with a timeout (seconds). Raises TimeoutError on timeout."""
        if self._registry.get(name) is None:
            raise KeyError(name)
        handler = self._registry.get(name)
        assert handler is not None
        # Delegate execution to HandlerExecutor (strategy encapsulated)
        try:
            return self._executor.execute_with_timeout(handler, params, timeout=timeout)
        except TimeoutError:
            # Keep behavior expected by unit tests: raise the builtin
            # TimeoutError to callers of dispatch_with_timeout.
            logger.error("handler %s timed out after %s", name, timeout)
            raise

    def dispatch_command(
        self,
        command: Dict[str, Any],
        policy_check: Optional[PolicyChecker] = None,
    ) -> DispatcherResult:
        """Deprecated: delegate to CommandAdapter for normalization.

        Kept for backward compatibility; behavior unchanged — the
        implementation now delegates to `CommandAdapter` which houses the
        normalization and error handling logic.
        """
        # allow per-call override of the policy_check; otherwise use the
        # instance-level policy_check if provided
        # allow per-call override; if not provided, instance-level policy_check is used
        effective_checker = policy_check or self._policy_check
        # run through policy strategy (non-blocking; adapter re-checks mapping)
        denial_reason = self._policy_strategy.check(effective_checker, command)
        if denial_reason:
            # mimic adapter error path without invoking CommandAdapter logic early
            return {
                "status": "error",
                "message": f"Blocked by policy: {denial_reason}",
                "error_code": "policy_denied",
            }
        adapter = CommandAdapter(self, policy_check=effective_checker)
        if self._instrumentation is not None:
            try:
                self._instrumentation.on_adapter_invoke(adapter.__class__.__name__, command.get("type", ""), command)
            except Exception:
                pass
        return adapter.dispatch_command(command)

    # --- Internal helpers ---
    def _invoke_service(self, service: Any, params: Dict[str, Any]) -> Any:
        """Best-effort invocation of a service function en fonction de sa signature.

        Règles simples:
        - Si la fonction attend un seul paramètre: lui passer `params`.
        - Sinon: faire correspondre chaque paramètre par nom via `params.get(name)`.
        - Paramètres obligatoires manquants -> ValueError.
        """
        sig = inspect.signature(service)
        if len(sig.parameters) == 1:
            sole = next(iter(sig.parameters.values()))
            if sole.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
                return service(params)
        # Build kwargs mapping
        kwargs: Dict[str, Any] = {}
        missing: List[str] = []
        for p in sig.parameters.values():
            if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
                continue
            if p.name in params:
                kwargs[p.name] = params[p.name]
            else:
                if p.default is inspect.Signature.empty:
                    missing.append(p.name)
        if missing:
            raise ValueError(f"missing required params for service {service.__name__}: {', '.join(missing)}")
        return service(**kwargs)


def register_default_handlers(dispatcher: Dispatcher) -> None:
    """Register a couple of minimal handlers useful for tests and defaults."""

    def add_primitive(params: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "primitive": params.get("type", "cube")}

    # allow overwrite to be idempotent in tests - some dispatcher
    # implementations (older shim) don't accept the `overwrite`
    # keyword. Try the modern call first and fall back to the
    # simpler signature for compatibility.
    try:
        dispatcher.register("add_primitive", add_primitive, overwrite=True)  # type: ignore[arg-type]
    except TypeError:
        dispatcher.register("add_primitive", add_primitive)

    # also register a small convenience helper expected by some tests
    def create_dice(params: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "primitive": "dice", "sides": params.get("sides", 6)}

    try:
        dispatcher.register("create_dice", create_dice, overwrite=True)  # type: ignore[arg-type]
    except TypeError:
        dispatcher.register("create_dice", create_dice)


__all__ = ["Dispatcher", "register_default_handlers"]

# Backwards compatibility: some tests and modules expected CommandDispatcher
# Annotate as a broadly-typed class variable so mypy accepts later reassignment
CommandDispatcher: type[Any] = Dispatcher
__all__.append("CommandDispatcher")

# Re-export exception types for backward compatibility
# Bind backwards-compatible names to the canonical exceptions so imports
# like `from blender_mcp.dispatchers.dispatcher import HandlerError` still work.
HandlerNotFound = CanonicalHandlerNotFoundError
HandlerError = CanonicalHandlerError
__all__.extend(["HandlerNotFound", "HandlerError"])


# Compatibility command-style dispatcher expected by older tests/tools; the
# compat wrapper is imported above and re-exported below for backward
# compatibility.
CommandDispatcher = _CommandDispatcherCompat
if "CommandDispatcher" not in __all__:
    __all__.append("CommandDispatcher")


# Stubbed external calls - tests will monkeypatch these at runtime
def run_bridge(
    user_req: str,
    config: Any,
    dispatcher: _CommandDispatcherCompat,
    use_api: bool = False,
    gemini_caller: Optional[Callable[..., Any]] = None,
    mcp_tool_caller: Optional[Callable[..., Any]] = None,
) -> None:
    """Run the Gemini->tool bridging flow.

    This function delegates to `BridgeService`. The concrete callers can be
    provided via `gemini_caller` and `mcp_tool_caller` parameters (dependency
    injection pattern). If not provided, defaults to module-level stubs from
    `bridge.py` for backwards compatibility with tests that monkeypatch those
    stubs.

    Args:
        user_req: User request string to pass to Gemini
        config: Configuration object
        dispatcher: Dispatcher instance to use for tool execution
        use_api: Whether to use API mode (passed to gemini_caller)
        gemini_caller: Optional callable that accepts (user_req, use_api) and
            returns a dict. If None, uses module-level `call_gemini_cli`.
        mcp_tool_caller: Optional callable that accepts (tool, params) and
            invokes remote MCP tools. If None, uses module-level `call_mcp_tool`.
    """
    # Use provided callables or fall back to module-level defaults for backwards
    # compatibility with existing tests that monkeypatch the module-level functions.
    _gemini = gemini_caller if gemini_caller is not None else call_gemini_cli
    _mcp_tool = mcp_tool_caller if mcp_tool_caller is not None else call_mcp_tool
    
    service = BridgeService(_gemini, _mcp_tool)
    return service.run(user_req, config, dispatcher, use_api=use_api)

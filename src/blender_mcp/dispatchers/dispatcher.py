"""Dispatcher utility for registering and dispatching BlenderMCP handlers.

This module is a relocated copy of the top-level `blender_mcp.dispatcher`.
Relative imports have been adjusted so this file lives inside the
`blender_mcp.dispatchers` package.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional

from ..errors import (
    ExecutionTimeoutError,
)
from ..errors import (
    HandlerError as CanonicalHandlerError,
)
from ..errors import (
    HandlerNotFoundError as CanonicalHandlerNotFoundError,
)
from ..types import DispatcherResult
from .abc import AbstractDispatcher
from .bridge import BridgeService, call_gemini_cli, call_mcp_tool
from .command_adapter import CommandAdapter
from .compat import CommandDispatcher as _CommandDispatcherCompat
from .executor import HandlerExecutor
from .policies import PolicyChecker
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

    def dispatch(self, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Call the handler named `name` with `params` and return its result.

        If the handler is not found, returns None.
        """
        fn = self._registry.get(name)
        if fn is None:
            logger.debug("no handler for %s", name)
            return None
        logger.debug("dispatching handler %s with params=%s", name, params)
        try:
            return fn(params or {})
        except Exception as exc:
            # wrap in HandlerError for compatibility with code that expects
            # handler exceptions to be wrapped
            logger.exception("handler %s raised", name)
            # Raise the canonical HandlerError so higher layers (adapters)
            # can map it consistently.
            raise CanonicalHandlerError(name, exc) from exc

    def dispatch_strict(self, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Like `dispatch` but raises KeyError if the handler is missing."""
        if self._registry.get(name) is None:
            logger.debug("dispatch_strict: missing handler %s", name)
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
            logger.error("handler %s timed out after %s", name, timeout)
            # Normalize timeout into a canonical ExecutionTimeoutError so callers
            # can map to stable error codes.
            raise ExecutionTimeoutError()

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
        adapter = CommandAdapter(self, policy_check=(policy_check or self._policy_check))
        return adapter.dispatch_command(command)


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
) -> None:
    """Run the Gemini->tool bridging flow.

    This function delegates to `BridgeService`. The concrete callers
    are the module-level stubs defined in `bridge.py` so tests can
    monkeypatch `blender_mcp.dispatchers.bridge.call_gemini_cli` and
    `blender_mcp.dispatchers.bridge.call_mcp_tool` as needed.
    """
    # Use the module-level callables (imported from bridge at module import
    # time) so tests can monkeypatch `dispatcher.call_gemini_cli` and
    # `dispatcher.call_mcp_tool` easily.
    service = BridgeService(call_gemini_cli, call_mcp_tool)
    return service.run(user_req, config, dispatcher, use_api=use_api)

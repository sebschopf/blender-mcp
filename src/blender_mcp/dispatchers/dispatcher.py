"""Dispatcher utility for registering and dispatching BlenderMCP handlers.

This module is a relocated copy of the top-level `blender_mcp.dispatcher`.
Relative imports have been adjusted so this file lives inside the
`blender_mcp.dispatchers` package.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutTimeout
from typing import Any, Callable, Dict, List, Optional, cast

from ..types import DispatcherResult

logger = logging.getLogger(__name__)


# Backwards-compatible simple exception types used by some tests/modules
class HandlerNotFound(Exception):
    """Raised when a dispatch target cannot be found."""


class HandlerError(Exception):
    """Wraps exceptions raised by handlers.

    Attributes:
        name: the handler name that raised
        original: the original exception instance
    """

    def __init__(self, name: str, original: Exception) -> None:
        super().__init__(f"Handler '{name}' raised {original!r}")
        self.name = name
        self.original = original


Handler = Callable[[Dict[str, Any]], Any]


class Dispatcher:
    def __init__(self) -> None:
        self._handlers: Dict[str, Handler] = {}

    def register(self, name: str, fn: Handler, *, overwrite: bool = False) -> None:
        """Register a handler by name.

        By default `overwrite=False` and attempting to register an already
        existing name will raise ValueError (audit-friendly). Set
        `overwrite=True` to replace existing handlers.
        """
        if name in self._handlers and not overwrite:
            raise ValueError(f"handler already registered for {name}")
        self._handlers[name] = fn
        logger.debug("registered handler %s (overwrite=%s)", name, overwrite)

    def unregister(self, name: str) -> None:
        """Remove a handler if present (no-op if missing)."""
        self._handlers.pop(name, None)
        logger.debug("unregistered handler %s", name)

    def list_handlers(self) -> List[str]:
        """Return a sorted list of registered handler names."""
        return sorted(self._handlers.keys())

    def dispatch(self, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Call the handler named `name` with `params` and return its result.

        If the handler is not found, returns None.
        """
        fn = self._handlers.get(name)
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
            raise HandlerError(name, exc) from exc

    def dispatch_strict(
        self, name: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Like `dispatch` but raises KeyError if the handler is missing."""
        if name not in self._handlers:
            logger.debug("dispatch_strict: missing handler %s", name)
            raise KeyError(name)
        return self.dispatch(name, params)

    def dispatch_with_timeout(
        self, name: str, params: Optional[Dict[str, Any]] = None, timeout: float = 5.0
    ) -> Any:
        """Call handler with a timeout (seconds). Raises TimeoutError on timeout."""
        if name not in self._handlers:
            raise KeyError(name)
        handler = self._handlers[name]
        with ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(handler, params or {})
            try:
                return fut.result(timeout=timeout)
            except FutTimeout as e:
                logger.error("handler %s timed out after %s", name, timeout)
                raise TimeoutError(
                    f"handler {name} timed out after {timeout} seconds"
                ) from e

    def dispatch_command(self, command: Dict[str, Any]) -> DispatcherResult:
        """Adapter to accept command dicts and return normalized responses.

        Expected shape: {"type": <str>, "params": {...}}
        Returns: {"status":"success","result":...} or {"status":"error","message":...}
        """
        # command is expected to be a mapping-like object; normalize access
        if not isinstance(command, dict):
            return {"status": "error", "message": "Invalid command format"}

        cmd_type_raw = command.get("type") or command.get("tool")
        if not isinstance(cmd_type_raw, str):
            return {"status": "error", "message": "Invalid or missing command type"}
        cmd_type = cmd_type_raw

        params_raw = command.get("params", {}) or {}
        params: Dict[str, Any] = params_raw if isinstance(params_raw, dict) else {}

        if cmd_type not in self._handlers:
            return {"status": "error", "message": f"Unknown command type: {cmd_type}"}

        try:
            result = self._handlers[cmd_type](params)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.exception("error while executing handler %s", cmd_type)
            return {"status": "error", "message": str(e)}


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


# Compatibility command-style dispatcher expected by older tests/tools
class _CommandDispatcherCompat:
    """Lightweight compatibility wrapper exposing a simple register/dispatch API.

    API:
      - register(name, handler)
      - unregister(name)
      - list_handlers()
      - dispatch(name, params=None, config=None) -> result

    Handlers registered here are expected to accept (params, config) but
    wrappers are tolerant and will pass whatever positional args the
    handler accepts.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, handler: Callable[..., Any]) -> None:
        self._handlers[name] = handler

    def unregister(self, name: str) -> None:
        self._handlers.pop(name, None)

    def list_handlers(self) -> List[str]:
        return sorted(self._handlers.keys())

    def dispatch(
        self,
        name: str,
        params: Optional[Dict[str, Any]] = None,
        config: Optional[Any] = None,
    ) -> Any:
        if name not in self._handlers:
            raise KeyError(name)
        handler = self._handlers[name]
        # Try calling with (params, config), fall back to single-arg or no-arg
        try:
            return handler(params, config)
        except TypeError:
            try:
                return handler(params)
            except TypeError:
                return handler()


# export the compatibility CommandDispatcher name
CommandDispatcher = _CommandDispatcherCompat
if "CommandDispatcher" not in __all__:
    __all__.append("CommandDispatcher")


# Stubbed external calls - tests will monkeypatch these at runtime
def call_gemini_cli(user_req: str, use_api: bool = False):
    """Placeholder for the Gemini client call; tests monkeypatch this."""
    raise NotImplementedError("call_gemini_cli should be provided by environment/tests")


def call_mcp_tool(tool: str, params: Dict[str, Any]):
    """Placeholder for a function that calls an MCP tool remotely; tests monkeypatch this."""
    raise NotImplementedError("call_mcp_tool should be provided by environment/tests")


def run_bridge(
    user_req: str,
    config: Any,
    dispatcher: _CommandDispatcherCompat,
    use_api: bool = False,
) -> None:
    """Run the Gemini->tool bridging flow.

    This function asks Gemini (via `call_gemini_cli`) to map a user
    request to either a clarifying question or a tool mapping. If the
    mapping names a tool registered on `dispatcher`, the corresponding
    handler is invoked with (params, config). If the mapping specifies
    a remote MCP tool, `call_mcp_tool` is used.
    """
    resp: Any = call_gemini_cli(user_req, use_api=use_api)
    while True:
        # When resp is a mapping, cast it so static analyzers know types
        if isinstance(resp, dict) and "clarify" in resp:
            data = cast(Dict[str, Any], resp)
            prompts_raw = data.get("clarify", []) or []
            # normalize prompts to list[str]
            if isinstance(prompts_raw, list):
                prompts: List[str] = [str(p) for p in prompts_raw]
            else:
                prompts = [str(prompts_raw)]

            for p in prompts:
                try:
                    ans = input(p + " ")
                except Exception:
                    ans = ""
                resp = call_gemini_cli(ans or user_req, use_api=use_api)
                # loop continues and will handle the new resp
        elif isinstance(resp, dict) and "tool" in resp:
            data = cast(Dict[str, Any], resp)
            tool_raw = data.get("tool")
            params_raw = data.get("params", {}) or {}
            tool = str(tool_raw) if tool_raw is not None else ""
            params = params_raw if isinstance(params_raw, dict) else {}

            # if the dispatcher knows this tool, call the local handler
            if tool in dispatcher.list_handlers():
                dispatcher.dispatch(tool, params, config)
            else:
                # otherwise call remote MCP tool
                call_mcp_tool(tool, params)
            return
        else:
            # nothing to do
            return

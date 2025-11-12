import asyncio
import inspect
import logging
import threading
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Tuple

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from . import logging_utils

# Import the server module; it defines `mcp` and helpers but does not call run()
from . import server as srv
from .errors import (
    ExecutionTimeoutError,
    ExternalServiceError,
    HandlerNotFoundError,
    InvalidParamsError,
    PolicyDeniedError,
)
from .errors import (
    HandlerError as CanonicalHandlerError,
)

logger = logging.getLogger("BlenderMCPASGI")




def _map_exception_to_http(exc: Exception) -> Tuple[int, Dict[str, Any]]:
    """Map canonical internal exceptions to HTTP status code + payload."""
    if isinstance(exc, InvalidParamsError):
        return 400, {"message": str(exc), "error_code": "invalid_params"}
    if isinstance(exc, HandlerNotFoundError):
        return 404, {"message": str(exc), "error_code": "not_found"}
    if isinstance(exc, PolicyDeniedError):
        return 403, {"message": str(exc), "error_code": "policy_denied"}
    if isinstance(exc, ExecutionTimeoutError):
        return 504, {"message": "Handler timed out", "error_code": "timeout"}
    if isinstance(exc, ExternalServiceError):
        return 502, {"message": str(exc), "error_code": "external_error"}
    if isinstance(exc, CanonicalHandlerError):
        return 500, {"message": str(exc), "error_code": "handler_error"}
    return 500, {"message": str(exc), "error_code": "internal_error"}


def _ensure_mcp_thread(app: FastAPI, server_module: Any) -> None:
    """Start the MCP thread for the app if it's not already running.

    Extracted from create_app to reduce function complexity for linters.
    """
    try:
        if getattr(app.state, "mcp_thread", None) is None or not getattr(
            app.state.mcp_thread, "is_alive", lambda: False
        )():
            app.state.mcp_thread = threading.Thread(
                target=lambda: server_module.main(),
                name="BlenderMCPThread",
                daemon=True,
            )
            app.state.mcp_thread.start()
            logger.info("Started BlenderMCP thread (lifespan)")
    except Exception:
        logger.exception("Failed to start BlenderMCP thread")


def _shutdown_mcp_thread(app: FastAPI) -> None:
    """Attempt to gracefully stop the MCP thread and join it.

    Extracted to make shutdown logic testable and reduce complexity.
    """
    try:
        stop_fn = getattr(app.state.server_module, "stop", None) or getattr(
            app.state.server_module, "shutdown", None
        )
        if callable(stop_fn):
            try:
                stop_fn()
            except Exception:
                logger.exception("Error while calling server_module.stop()/shutdown()")

        # Use a local variable with an isinstance check to help static analysis
        mcp_thread = getattr(app.state, "mcp_thread", None)
        if isinstance(mcp_thread, threading.Thread) and mcp_thread.is_alive():
            mcp_thread.join(timeout=2.0)
            if mcp_thread.is_alive():
                logger.warning("MCP thread still alive after join timeout")
    except Exception:
        logger.exception("Error during MCP thread shutdown")
 
 
def _extract_tools_from_registry(mcp_obj: Any) -> list[Dict[str, Any]]:
    """Try to extract tool names from common registry patterns."""
    out: list[Dict[str, Any]] = []
    for attr in ("tools", "registry"):
        if hasattr(mcp_obj, attr):
            reg = getattr(mcp_obj, attr)
            try:
                for name in getattr(reg, "keys", lambda: reg)():
                    out.append({"name": str(name)})
                return out
            except Exception:
                pass
    return out


def _extract_module_level_tools(server: Any) -> list[Dict[str, Any]]:
    out: list[Dict[str, Any]] = []
    for name, func in inspect.getmembers(server, inspect.isfunction):
        if getattr(func, "__module__", "") == server.__name__:
            try:
                sig = str(inspect.signature(func))
            except Exception:
                sig = "()"
            doc = (func.__doc__ or "").strip().split("\n")[0] if func.__doc__ else ""
            out.append({"name": name, "signature": sig, "doc": doc})
    return out


def make_health(server_module: Any):
    def health() -> Dict[str, Any]:
        """Return basic health information about the MCP server and Blender connection."""
        try:
            server_module.get_blender_connection()
            return {"status": "ok", "blender": "connected"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return health


def make_list_tools(server_module: Any):
    def list_tools() -> Dict[str, Any]:
        """Return a list of available tools exposed by the MCP server."""
        try:
            tools_info = []
            server = server_module
            if hasattr(server, "mcp"):
                tools_info.extend(_extract_tools_from_registry(server.mcp))

            tools_info.extend(_extract_module_level_tools(server))

            return {"status": "ok", "tools": tools_info}
        except Exception as e:
            logger.exception("Failed to list tools")
            raise HTTPException(status_code=500, detail=str(e))


def make_call_tool(server_module: Any):
    async def call_tool(name: str, request: Request) -> Any:
        try:
            body = await request.json()
        except Exception:
            body = {}

        params = body.get("params") or {}

        server = server_module
        func = getattr(server, name, None)
        if func is None or not callable(func):
            raise HTTPException(status_code=404, detail=f"Tool '{name}' not found")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(None, **params)
            else:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, lambda: func(None, **params))

            encoded = jsonable_encoder(result)
            try:
                logging_utils.log_action(
                    "asgi",
                    "call_tool",
                    {"tool": name, "params": params},
                    {"status": "ok", "result": encoded},
                )
            except Exception:
                logger.exception("Failed to emit audit log for successful tool call")

            return {"status": "ok", "result": encoded}
        except Exception as e:
            logger.exception("Error calling tool %s", name)

            status_code, payload = _map_exception_to_http(e)
            body = {"status": "error", **payload}

            try:
                logging_utils.log_action(
                    "asgi",
                    "call_tool_error",
                    {"tool": name, "params": params},
                    body,
                )
            except Exception:
                logger.exception("Failed to emit audit log for tool error")

            return JSONResponse(status_code=status_code, content=jsonable_encoder(body))

    return call_tool
def create_app(server_module: Optional[object] = None) -> FastAPI:
    """Factory to create a FastAPI app bound to a specific `server_module`.

    This makes the adapter test-friendly: tests can pass a fake server module
    (with `main`, `get_blender_connection`, etc.) and isolate the MCP thread per-app.
    """
    server_module = server_module or srv

    # Note: MCP runner is started via a background thread created by
    # _ensure_mcp_thread(app, server_module). We intentionally avoid an
    # inner helper here to keep create_app small; the thread target calls
    # server_module.main() at runtime.

    @asynccontextmanager
    async def _lifespan(app: FastAPI):
        """Start the MCP server in a background thread for the app lifespan."""
        # per-app state for isolation in tests
        app.state.server_module = server_module
        app.state.mcp_thread = None

        # start the mcp thread if needed (helper extracted to reduce complexity)
        _ensure_mcp_thread(app, server_module)

        try:
            yield
        finally:
            # shutdown helper handles graceful stop and join
            _shutdown_mcp_thread(app)

    app = FastAPI(title="BlenderMCP ASGI adapter", lifespan=_lifespan)
    # Provide sane defaults so code (and tests) can access `app.state.server_module`
    # even if the lifespan/startup hasn't executed yet (TestClient behavior varies
    # by version and context manager usage).
    app.state.server_module = server_module
    app.state.mcp_thread = None

    # Register routes using small factory functions so create_app stays small
    app.get("/health")(make_health(server_module))
    app.get("/tools")(make_list_tools(server_module))
    app.post("/tools/{name}")(make_call_tool(server_module))

    return app


# Backwards-compatible module-level app
app = create_app(srv)

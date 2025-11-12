import asyncio
import inspect
import logging
import threading
from contextlib import asynccontextmanager
from typing import Any, Dict, Tuple

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

mcp_thread = None


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


def _run_mcp():
    try:
        # srv.main() calls mcp.run() and blocks until shutdown
        srv.main()
    except Exception:
        logger.exception("mcp.run() exited with an error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the MCP server in a background thread for the app lifespan.

    Using FastAPI lifespan ensures TestClient triggers startup/shutdown and
    avoids the deprecated `on_event('startup')` handler.
    """
    global mcp_thread
    try:
        if mcp_thread is None or not mcp_thread.is_alive():
            mcp_thread = threading.Thread(target=_run_mcp, name="BlenderMCPThread", daemon=True)
            mcp_thread.start()
            logger.info("Started BlenderMCP thread (lifespan)")
    except Exception:
        logger.exception("Failed to start BlenderMCP thread")

    try:
        yield
    finally:
        # Attempt graceful shutdown if the server exposes a stop function.
        try:
            stop_fn = getattr(srv, "stop", None) or getattr(srv, "shutdown", None)
            if callable(stop_fn):
                try:
                    stop_fn()
                except Exception:
                    logger.exception("Error while calling srv.stop()/shutdown()")

            if mcp_thread is not None and mcp_thread.is_alive():
                mcp_thread.join(timeout=2.0)
                if mcp_thread.is_alive():
                    logger.warning("MCP thread still alive after join timeout")
        except Exception:
            logger.exception("Error during MCP thread shutdown")


app = FastAPI(title="BlenderMCP ASGI adapter", lifespan=lifespan)


@app.get("/health")
def health():
    """Return basic health information about the MCP server and Blender connection."""
    try:
        # Try to get (or create) a Blender connection — this will raise if Blender isn't available
        srv.get_blender_connection()
        return {"status": "ok", "blender": "connected"}
    except Exception as e:
        # keep health lightweight and backward-compatible
        return {"status": "error", "message": str(e)}


@app.get("/tools")
def list_tools():
    """Return a list of available tools exposed by the MCP server.

    The response format is {"status":"ok", "tools": [{"name":..., "signature":..., "doc":...}, ...]}
    This endpoint attempts to use the MCP instance if it exposes a registry; otherwise it
    falls back to inspecting the server module for callable functions.
    """
    try:
        tools_info = []
        # Try to extract a registry from the mcp instance if available
        if hasattr(srv, "mcp"):
            mcp_obj = srv.mcp
            # Common registry patterns: dict-like attribute 'tools' or 'registry'
            for attr in ("tools", "registry"):
                if hasattr(mcp_obj, attr):
                    reg = getattr(mcp_obj, attr)
                    try:
                        # If it's a dict-like registry
                        for name in getattr(reg, "keys", lambda: reg)():
                            tools_info.append({"name": str(name)})
                        break
                    except Exception:
                        # ignore and fallback
                        pass

        # Fallback: inspect module-level functions defined in srv
        for name, func in inspect.getmembers(srv, inspect.isfunction):
            if getattr(func, "__module__", "") == srv.__name__:
                try:
                    sig = str(inspect.signature(func))
                except Exception:
                    sig = "()"
                doc = (func.__doc__ or "").strip().split("\n")[0] if func.__doc__ else ""
                tools_info.append(
                    {
                        "name": name,
                        "signature": sig,
                        "doc": doc,
                    }
                )

        return {"status": "ok", "tools": tools_info}
    except Exception as e:
        logger.exception("Failed to list tools")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/{name}")
async def call_tool(name: str, request: Request) -> Any:
    """Call a tool function defined in `blender_mcp.server` by name.

    Body JSON: { "params": { ... } }
    Returns JSON: { "status": "ok", "result": ... } or error.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    params = body.get("params") or {}

    func = getattr(srv, name, None)
    if func is None or not callable(func):
        raise HTTPException(status_code=404, detail=f"Tool '{name}' not found")

    try:
        # Support both sync and async tool functions
        if asyncio.iscoroutinefunction(func):
            result = await func(None, **params)
        else:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, lambda: func(None, **params))

        # emit audit log for success (do not let logging failure break the response)
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

        # Map canonical exceptions to HTTP status codes and include stable error_code
        status_code, payload = _map_exception_to_http(e)
        body = {"status": "error", **payload}

        # audit log the failure (best-effort)
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

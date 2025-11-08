import asyncio
import inspect
import logging
import threading
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder

# Import the server module; it defines `mcp` and helpers but does not call run()
from . import server as srv

logger = logging.getLogger("BlenderMCPASGI")

app = FastAPI(title="BlenderMCP ASGI adapter")

mcp_thread = None


def _run_mcp():
    try:
        # srv.main() calls mcp.run() and blocks until shutdown
        srv.main()
    except Exception:
        logger.exception("mcp.run() exited with an error")


@app.on_event("startup")
def _startup():
    global mcp_thread
    # Start MCP server in a daemon thread so FastAPI/uvicorn can run alongside it
    if mcp_thread is None or not mcp_thread.is_alive():
        mcp_thread = threading.Thread(
            target=_run_mcp, name="BlenderMCPThread", daemon=True
        )
        mcp_thread.start()
        logger.info("Started BlenderMCP thread")


@app.get("/health")
def health():
    """Return basic health information about the MCP server and Blender connection."""
    try:
        # Try to get (or create) a Blender connection — this will raise if Blender isn't available
        srv.get_blender_connection()
        return {"status": "ok", "blender": "connected"}
    except Exception as e:
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
                doc = (
                    (func.__doc__ or "").strip().split("\n")[0] if func.__doc__ else ""
                )
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

        return {"status": "ok", "result": jsonable_encoder(result)}
    except Exception as e:
        logger.exception("Error calling tool %s", name)
        raise HTTPException(status_code=500, detail=str(e))

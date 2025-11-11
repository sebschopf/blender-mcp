import json
import os
import tempfile
from typing import Any, Callable, Dict, TypeVar, cast

# Avoid importing `blender_mcp.server` or `mcp` at module-import time so
# CI/tests do not require Blender or the MCP runtime. We provide a small
# local Image class when the real one isn't available and decorate tools
# with a no-op decorator when `mcp` isn't present.
try:
    from mcp.server.fastmcp import Context
except Exception:  # pragma: no cover - fallback for test environments
    # Provide a minimal generic Context fallback so test environments and
    # static analyzers can subscript it (e.g. Context[Any, Any, Any]).
    from typing import Generic, TypeVar

    _C1 = TypeVar("_C1")
    _C2 = TypeVar("_C2")
    _C3 = TypeVar("_C3")

    class Context(Generic[_C1, _C2, _C3]):  # type: ignore
        """Lightweight generic shim used only when the real MCP Context
        type cannot be imported (tests / CI).

        It's intentionally empty; callers only need it to be subscriptable
        and to appear as a valid type in annotations.
        """

        pass


class Image:  # simple fallback used in tests
    def __init__(self, data: bytes, format: str = "png") -> None:
        self.data = data
        self.format = format


F = TypeVar("F", bound=Callable[..., Any])


def _get_mcp_tool_decorator() -> Callable[..., Callable[[Callable[..., Any]], Callable[..., Any]]]:
    try:
        from . import server as _server

        mcp = getattr(_server, "mcp", None)
        if mcp is not None:
            # type: ignore[return-value]
            return getattr(mcp, "tool", lambda *a, **k: (lambda f: f))
    except Exception:
        pass

    # fallback no-op decorator
    def _noop(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def _inner(f: Callable[..., Any]) -> Callable[..., Any]:
            return f

        return _inner

    return _noop


_tool: Callable[..., Callable[[Callable[..., Any]], Callable[..., Any]]] = _get_mcp_tool_decorator()


def _get_blender_connection():
    """Lazily import and return server.get_blender_connection.

    This avoids importing the potentially broken `server` module at
    top-level in tests; callers/tests can patch this function.
    """
    try:
        from .server import get_blender_connection as _g

        return _g
    except Exception:  # pragma: no cover - in tests we'll patch this

        def _missing():
            raise ConnectionError("Blender server not available")

        return _missing


def get_blender_connection():
    """Public shim so tests can patch `blender_mcp.tools.get_blender_connection`.

    Internally this delegates to the lazily-resolved server function.
    """
    return _get_blender_connection()()


# Provide a lightweight `mcp` shim so modules can import `mcp.tool()` / `mcp.prompt()`
# without requiring the real MCP runtime at import-time. In runtime the real
# `mcp` object (if present) will be used by other code paths; this shim keeps
# static analyzers and tests happy.
class _MCPShim:
    def tool(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        # Cast since _tool may be untyped at runtime; we guarantee a decorator-like
        # callable is returned by _get_mcp_tool_decorator.
        return cast(Callable[..., Callable[[Callable[..., Any]], Callable[..., Any]]], _tool)(*args, **kwargs)

    def prompt(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return cast(Callable[..., Callable[[Callable[..., Any]], Callable[..., Any]]], _tool)(*args, **kwargs)


mcp = _MCPShim()


@_tool()
def get_scene_info(ctx: Context[Any, Any, Any]) -> str:
    try:
        blender = get_blender_connection()
        result = cast(Dict[str, Any], blender.send_command("get_scene_info"))
        return json.dumps(result, indent=2)
    except Exception as e:
        # try to log if server.logger is available
        try:
            from . import server as _server

            _log = getattr(_server, "logger", None)
            if _log is not None:
                _log.error(f"Error getting scene info from Blender: {str(e)}")
        except Exception:
            pass
        return f"Error getting scene info: {str(e)}"


@_tool()
def get_object_info(ctx: Context[Any, Any, Any], object_name: str) -> str:
    try:
        blender = get_blender_connection()
        result = cast(
            Dict[str, Any],
            blender.send_command("get_object_info", {"name": object_name}),
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        try:
            from . import server as _server

            _log = getattr(_server, "logger", None)
            if _log is not None:
                _log.error(f"Error getting object info from Blender: {str(e)}")
        except Exception:
            pass
        return f"Error getting object info: {str(e)}"


@_tool()
def get_viewport_screenshot(ctx: Context[Any, Any, Any], max_size: int = 800) -> Image:
    try:
        blender = get_blender_connection()
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"blender_screenshot_{os.getpid()}.png")
        result = cast(
            Dict[str, Any],
            blender.send_command(
                "get_viewport_screenshot",
                {"max_size": max_size, "filepath": temp_path, "format": "png"},
            ),
        )
        if "error" in result:
            raise Exception(result["error"])
        if not os.path.exists(temp_path):
            raise Exception("Screenshot file was not created")
        with open(temp_path, "rb") as f:
            image_bytes = f.read()
        os.remove(temp_path)
        return Image(data=image_bytes, format="png")
    except Exception as e:
        try:
            from . import server as _server

            _log = getattr(_server, "logger", None)
            if _log is not None:
                _log.error(f"Error capturing screenshot: {str(e)}")
        except Exception:
            pass
        raise Exception(f"Screenshot failed: {str(e)}")


@_tool()
def execute_blender_code(ctx: Context[Any, Any, Any], code: str) -> str:
    try:
        blender = get_blender_connection()
        result = cast(Dict[str, Any], blender.send_command("execute_code", {"code": code}))
        return f"Code executed successfully: {result.get('result', '')}"
    except Exception as e:
        try:
            from . import server as _server

            _log = getattr(_server, "logger", None)
            if _log is not None:
                _log.error(f"Error executing code: {str(e)}")
        except Exception:
            pass
        return f"Error executing code: {str(e)}"

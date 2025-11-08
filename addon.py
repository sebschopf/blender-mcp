"""Minimal Blender add-on shim.

This file intentionally stays minimal and import-safe so it can be imported in
non-Blender environments (tests, CI). The real Blender UI and operators live
in `blender_mcp.blender_ui` and are imported lazily by register()/unregister().
"""

bl_info = {
    "name": "Blender MCP",
    "author": "BlenderMCP",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > BlenderMCP",
    "description": "Connect Blender to Gemini via MCP",
    "category": "Interface",
}


def _lazy_attr(module: str, name: str):
    """Import module lazily and return attribute or None on failure."""
    try:
        import importlib

        mod = importlib.import_module(module)
        return getattr(mod, name, None)
    except Exception:
        return None


def register():
    """Delegate registration to `blender_mcp.blender_ui.register` when present.

    This keeps the top-level module importable in environments without Blender.
    """
    fn = _lazy_attr("blender_mcp.blender_ui", "register")
    if callable(fn):
        try:
            fn()
            return
        except Exception as e:
            # Prefer noisy failure during development rather than silent import errors
            print(f"Error registering blender_mcp UI: {e}")


def unregister():
    """Delegate unregistration to `blender_mcp.blender_ui.unregister` when present."""
    fn = _lazy_attr("blender_mcp.blender_ui", "unregister")
    if callable(fn):
        try:
            fn()
            return
        except Exception as e:
            print(f"Error unregistering blender_mcp UI: {e}")


# Try to expose the packaged server implementation when available; otherwise
# provide a clear runtime error on instantiation so external scripts see a
# helpful message.
try:
    from blender_mcp.server import BlenderMCPServer  # type: ignore
except Exception:
    class BlenderMCPServer:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise RuntimeError("BlenderMCPServer is unavailable; install the package version")


if __name__ == "__main__":
    register()

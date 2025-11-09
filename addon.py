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


# Expose a lazy wrapper for the packaged server implementation.
#
# Rationale: avoid importing `blender_mcp.server` at module import time so the
# add-on remains import-safe in headless/test environments. The wrapper tries
# to import the real implementation when instantiated and delegates to it.
class BlenderMCPServer:
    """Lazy wrapper around the real BlenderMCPServer implementation.

    On instantiation, attempt to import `blender_mcp.server.BlenderMCPServer` and
    create a delegate instance. If the import fails, raise a RuntimeError with a
    clear message.
    """

    def __init__(self, *args, **kwargs):
        try:
            from importlib import import_module

            mod = import_module("blender_mcp.server")
            Real = getattr(mod, "BlenderMCPServer")
            # instantiate the real server and keep as delegate
            self._delegate = Real(*args, **kwargs)
        except Exception as e:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "BlenderMCPServer is unavailable; install the package version"
            ) from e

    def __getattr__(self, item):
        # Delegate attribute access to the real server instance
        return getattr(self._delegate, item)


if __name__ == "__main__":
    register()

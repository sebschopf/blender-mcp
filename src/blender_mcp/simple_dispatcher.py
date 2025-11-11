"""Top-level compatibility façade re-exporting the dispatcher package.

The implementation is now in ``blender_mcp.dispatchers``.
"""

from .dispatchers.simple_dispatcher import Dispatcher, register_default_handlers  # noqa: F401

__all__ = ["Dispatcher", "register_default_handlers"]
"""Top-level compatibility façade re-exporting the dispatcher package.

The implementation is now in `blender_mcp.dispatchers`.
"""


__all__ = ["Dispatcher", "register_default_handlers"]

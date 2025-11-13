"""Top-level compatibility façade re-exporting the dispatcher package.

The implementation is now in ``blender_mcp.dispatchers``.
"""

import warnings as _warnings

from .dispatchers.simple_dispatcher import Dispatcher, register_default_handlers  # noqa: F401

_warnings.warn(
	"blender_mcp.simple_dispatcher is deprecated; use blender_mcp.dispatchers instead.",
	DeprecationWarning,
	stacklevel=2,
)

__all__ = ["Dispatcher", "register_default_handlers"]
"""Top-level compatibility façade re-exporting the dispatcher package.

The implementation is now in `blender_mcp.dispatchers`.
"""


__all__ = ["Dispatcher", "register_default_handlers"]

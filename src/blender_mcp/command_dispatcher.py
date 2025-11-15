"""Top-level compatibility façade for the old `command_dispatcher` module.

This module exists to preserve a soft transition period: importing
``blender_mcp.command_dispatcher`` emits a DeprecationWarning and re-exports
the implementation from ``blender_mcp.dispatchers.command_dispatcher``.
"""

import warnings as _warnings

from .dispatchers.command_dispatcher import CommandDispatcher  # noqa: F401

_warnings.warn(
    "blender_mcp.command_dispatcher is deprecated; use blender_mcp.dispatchers.command_dispatcher",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["CommandDispatcher"]

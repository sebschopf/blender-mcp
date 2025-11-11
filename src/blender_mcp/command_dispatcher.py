"""Top-level re-export of the `CommandDispatcher` into the new package.

The implementation lives in ``blender_mcp.dispatchers.command_dispatcher``.
"""

from .dispatchers.command_dispatcher import CommandDispatcher  # noqa: F401

__all__ = ["CommandDispatcher"]
"""Top-level re-export of the `CommandDispatcher` into the new package.

The implementation now lives in `blender_mcp.dispatchers.command_dispatcher`.
Keeping this thin façade ensures existing imports continue working.
"""


__all__ = ["CommandDispatcher"]

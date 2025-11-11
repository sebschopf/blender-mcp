"""Top-level compatibility façade for the `servers` package.

Expose the historically-imported names while the real code lives under
``blender_mcp.servers``.
"""

from .servers.server import BlenderMCPServer, _process_bbox  # noqa: F401

__all__ = ["_process_bbox", "BlenderMCPServer"]
"""Top-level compatibility façade for the `servers` package.

The implementations live under `blender_mcp.servers`. Keeping a thin
façade here preserves existing imports used by tests and external
consumers while we reorganize the code.
"""


__all__ = ["_process_bbox", "BlenderMCPServer"]

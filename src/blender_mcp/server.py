"""Top-level compatibility façade for the `servers` package.

Expose the historically-imported names while the real code lives under
``blender_mcp.servers``.
"""

import warnings as _warnings

from .servers.server import BlenderMCPServer, _process_bbox  # noqa: F401
import warnings as _warnings

_warnings.warn(
	"blender_mcp.server is a compatibility façade; import from blender_mcp.servers.server instead.",
	DeprecationWarning,
	stacklevel=2,
)

_warnings.warn(
	"blender_mcp.server is a compatibility façade; import from blender_mcp.servers.server instead.",
	DeprecationWarning,
	stacklevel=2,
)

__all__ = ["_process_bbox", "BlenderMCPServer"]
"""Top-level compatibility façade for the `servers` package.

The implementations live under `blender_mcp.servers`. Keeping a thin
façade here preserves existing imports used by tests and external
consumers while we reorganize the code.
"""


__all__ = ["_process_bbox", "BlenderMCPServer"]

"""Top-level compatibility façade for the `servers` package shim.

Implementation moved to `blender_mcp.servers.shim` to consolidate server
code under one package. This façade keeps existing imports working.
"""

from .servers.shim import BlenderMCPServer, _process_bbox  # noqa: F401
import warnings as _warnings

_warnings.warn(
	"blender_mcp.server_shim is deprecated; use blender_mcp.servers.shim instead.",
	DeprecationWarning,
	stacklevel=2,
)

__all__ = ["BlenderMCPServer", "_process_bbox"]
"""Top-level compatibility façade for the `servers` package shim.

Implementation moved to `blender_mcp.servers.shim` to consolidate server
code under one package. This façade keeps existing imports working.
"""


__all__ = ["BlenderMCPServer", "_process_bbox"]

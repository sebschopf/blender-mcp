"""Archived copy of the top-level server_shim façade.

Snapshot of `src/blender_mcp/server_shim.py` for history/reference.
"""

from .servers.shim import BlenderMCPServer, _process_bbox  # noqa: F401

__all__ = ["BlenderMCPServer", "_process_bbox"]

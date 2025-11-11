"""Archived copy of the top-level server façade.

Snapshot of `src/blender_mcp/server.py` kept in archive for reference.
"""

from .servers.server import BlenderMCPServer, _process_bbox  # noqa: F401

__all__ = ["_process_bbox", "BlenderMCPServer"]

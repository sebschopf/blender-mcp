"""Servers package public surface.

Re-export the relocated server helpers so callers can import from
`blender_mcp.servers`.
"""

from .server import BlenderMCPServer, _process_bbox
from .shim import BlenderMCPServer as ShimServer, _process_bbox as _shim_process_bbox
from .embedded_adapter import start_server_process, stop_server_process, is_running

__all__ = [
    "BlenderMCPServer",
    "_process_bbox",
    "ShimServer",
    "_shim_process_bbox",
    "start_server_process",
    "stop_server_process",
    "is_running",
]

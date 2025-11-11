"""Servers package public surface.

Re-export the relocated server helpers so callers can import from
`blender_mcp.servers`.
"""

from .embedded_adapter import is_running, start_server_process, stop_server_process
from .server import BlenderMCPServer, _process_bbox
from .shim import BlenderMCPServer as ShimServer
from .shim import _process_bbox as _shim_process_bbox

__all__ = [
    "BlenderMCPServer",
    "_process_bbox",
    "ShimServer",
    "_shim_process_bbox",
    "start_server_process",
    "stop_server_process",
    "is_running",
]

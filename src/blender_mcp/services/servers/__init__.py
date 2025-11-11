"""Package for server/transport related service code.

Place helpers that deal with sockets, ASGI, dispatchers and other transport
concerns here. These modules must not import `bpy` and should call service-
facing modules under `src/blender_mcp/services`.
"""

from blender_mcp.services.connection import (
    BlenderConnection,
    BlenderConnectionNetwork,
    ChunkedJSONReassembler,
    LengthPrefixedReassembler,
    SocketBlenderConnection,
)

from ... import server as _server

__all__ = [
    "_process_bbox",
    "BlenderMCPServer",
    "ChunkedJSONReassembler",
    "LengthPrefixedReassembler",
    "SocketBlenderConnection",
    "BlenderConnectionNetwork",
    "BlenderConnection",
]

# Re-export server helpers from top-level server module
_process_bbox = _server._process_bbox
BlenderMCPServer = _server.BlenderMCPServer

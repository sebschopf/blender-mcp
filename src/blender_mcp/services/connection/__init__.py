"""Public API for the connection package.

This package exposes small, focused modules that re-export the concrete
implementations from the package-level internal module. The split into
modules improves SOLID structure while keeping a stable public API.
"""

from .facade import BlenderConnection
from .framing import LengthPrefixedReassembler
from .network import BlenderConnectionNetwork
from .reassembler import ChunkedJSONReassembler
from .socket_conn import SocketBlenderConnection
from .receiver import ResponseReceiver
from .transport import CoreTransport, RawSocketTransport, Transport, select_transport

# Re-export canonical runtime accessor from consolidated implementation
try:
    # Prefer the canonical implementation in src/blender_mcp/connection_core.py
    from ...connection_core import get_blender_connection  # type: ignore
except Exception:
    # Fallback: leave get_blender_connection unavailable; callers may import
    # via the public tools shim which performs lazy resolution.
    get_blender_connection = None  # type: ignore

__all__ = [
    "ChunkedJSONReassembler",
    "LengthPrefixedReassembler",
    "SocketBlenderConnection",
    "BlenderConnectionNetwork",
    "BlenderConnection",
    "ResponseReceiver",
    "Transport",
    "RawSocketTransport",
    "CoreTransport",
    "select_transport",
    "get_blender_connection",
]

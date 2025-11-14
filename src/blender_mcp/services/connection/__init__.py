"""Public API for the connection package.

This package exposes small, focused modules that re-export the concrete
implementations from the package-level internal module. The split into
modules improves SOLID structure while keeping a stable public API.
"""

from .facade import BlenderConnection
from .framing import LengthPrefixedReassembler
from .network import BlenderConnectionNetwork
from .reassembler import ChunkedJSONReassembler
from .receiver import ResponseReceiver
from .socket_conn import SocketBlenderConnection
from .transport import CoreTransport, RawSocketTransport, Transport, select_transport

# Re-export canonical runtime accessor from consolidated implementation.
# Use lazy resolution at call sites instead of importing the legacy
# `connection_core` here to avoid import-order surprises during tests.
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

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

__all__ = [
    "ChunkedJSONReassembler",
    "LengthPrefixedReassembler",
    "SocketBlenderConnection",
    "BlenderConnectionNetwork",
    "BlenderConnection",
]

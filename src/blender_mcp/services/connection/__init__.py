"""Public API for the connection package.

This package exposes small, focused modules that re-export the concrete
implementations from the package-level internal module. The split into
modules improves SOLID structure while keeping a stable public API.
"""

from .reassembler import ChunkedJSONReassembler
from .framing import LengthPrefixedReassembler
from .socket_conn import SocketBlenderConnection
from .network import BlenderConnectionNetwork
from .facade import BlenderConnection

__all__ = [
    "ChunkedJSONReassembler",
    "LengthPrefixedReassembler",
    "SocketBlenderConnection",
    "BlenderConnectionNetwork",
    "BlenderConnection",
]

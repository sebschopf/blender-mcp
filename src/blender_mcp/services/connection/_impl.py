from __future__ import annotations

"""Deprecation shim for the connection package's internal impl module.

This file used to hold the concrete implementations. The implementation
now lives in `reassembler.py`, `framing.py`, `socket_conn.py`, `network.py`
and `facade.py`. Keep this small shim only to preserve compatibility for
callers that still import the implementation directly; it should be
removed once the repository no longer relies on this private module.
"""

from warnings import warn

warn(
    "blender_mcp.services.connection._impl is deprecated; import from "
    "blender_mcp.services.connection (public API) instead",
    DeprecationWarning,
)

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

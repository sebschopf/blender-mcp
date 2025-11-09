"""Backward-compatible re-export of the connection package.

This module re-exports the public types from ``blender_mcp.services.connection``
so existing imports like ``from blender_mcp.connection import BlenderConnection``
continue to work during and after the refactor.
"""

from .services.connection import (
    ChunkedJSONReassembler,
    LengthPrefixedReassembler,
    SocketBlenderConnection,
    BlenderConnectionNetwork,
    BlenderConnection,
)

__all__ = [
    "ChunkedJSONReassembler",
    "LengthPrefixedReassembler",
    "SocketBlenderConnection",
    "BlenderConnectionNetwork",
    "BlenderConnection",
]

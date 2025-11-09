from __future__ import annotations

"""Deprecation shim for the old implementation module.

Historically this file contained the concrete implementations for the
connection helpers. The code moved into the `services.connection` package
and this module now re-exports the public API as a short-lived shim so
external imports keep working during the migration.

This shim is safe to remove once callers stop importing the
implementation module directly. The goal is to no longer *need* any
``_impl.py`` files in the project; if you see this file in the tree we
should remove it once all consumers import from
``blender_mcp.services.connection`` or `blender_mcp.connection`.
"""

from warnings import warn

warn(
    "blender_mcp._connection_impl is deprecated; import from "
    "blender_mcp.services.connection or blender_mcp.connection instead",
    DeprecationWarning,
)

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

"""Clean, minimal server used as a temporary shim for tests.

Provides the same minimal API the tests expect: BlenderConnection,
get_blender_connection, server_lifespan and an optional `mcp` object.
This lives at the repository root to shadow the broken src package
during the ongoing refactor.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    # Prefer the consolidated implementation from the src package. Import the
    # concrete BlenderConnection implementation and helpers used by tests.
    from blender_mcp.connection_core import (
        BlenderConnection,
        get_blender_connection,
        server_lifespan,
    )
    import socket  # expose the stdlib socket module so tests can monkeypatch it
except Exception:
    # If import fails, re-raise to help diagnose environment issues.
    raise


try:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("BlenderMCP", lifespan=server_lifespan)
except Exception:
    mcp = None


__all__ = [
    "BlenderConnection",
    "get_blender_connection",
    "server_lifespan",
    "mcp",
]

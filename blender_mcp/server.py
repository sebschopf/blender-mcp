"""Clean, minimal server used as a temporary shim for tests.

Provides the same minimal API the tests expect: BlenderConnection,
get_blender_connection, server_lifespan and an optional `mcp` object.
This lives at the repository root to shadow the broken src package
during the ongoing refactor.
"""

from __future__ import annotations

import logging
from typing import Any, Optional
import warnings as _warnings

logger = logging.getLogger(__name__)

_warnings.warn(
    (
        "The top-level blender_mcp.server shim is temporary and deprecated; "
        "use blender_mcp.servers.server and related APIs. This shim will be removed."
    ),
    DeprecationWarning,
    stacklevel=2,
)

try:
    # Prefer the consolidated implementation from the src package. Import the
    # concrete BlenderConnection implementation and helpers used by tests.

    from blender_mcp.connection_core import (
        BlenderConnection,
        get_blender_connection,
        server_lifespan,
    )
except Exception:
    # If import fails, re-raise to help diagnose environment issues.
    raise


try:
    from mcp.server.fastmcp import FastMCP
    # pre-declare a possibly-None variable so type checkers understand the
    # runtime pattern where mcp may be unavailable in some environments.
    mcp: Optional[Any] = None
    mcp = FastMCP("BlenderMCP", lifespan=server_lifespan)
except Exception:
    mcp = None


__all__ = [
    "BlenderConnection",
    "get_blender_connection",
    "server_lifespan",
    "mcp",
]

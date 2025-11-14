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


def _load_connection_core():
    """Lazily import the canonical connection_core module.

    Avoid importing this at module import time to reduce the chance of
    duplicate-module identity problems when tests manipulate ``sys.path``.
    """
    import importlib

    return importlib.import_module("blender_mcp.connection_core")


try:
    from mcp.server.fastmcp import FastMCP

    # pre-declare a possibly-None variable so type checkers understand the
    # runtime pattern where mcp may be unavailable in some environments.
    mcp: Optional[Any] = None
    try:
        # Resolve the server_lifespan lazily from the canonical module.
        server_lifespan = getattr(_load_connection_core(), "server_lifespan")
        mcp = FastMCP("BlenderMCP", lifespan=server_lifespan)
    except Exception:
        mcp = None
except Exception:
    mcp = None


__all__ = [
    "get_blender_connection",
    "mcp",
]


def get_blender_connection():
    """Return the canonical `get_blender_connection` from `connection_core`.

    This function is intentionally lazy to avoid importing the legacy
    compatibility module at test-import time.
    """
    return getattr(_load_connection_core(), "get_blender_connection")()

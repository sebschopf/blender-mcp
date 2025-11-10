"""Clean, minimal server used as a temporary shim for tests.

Provides the same minimal API the tests expect: BlenderConnection,
get_blender_connection, server_lifespan and an optional `mcp` object.
This lives at the repository root to shadow the broken src package
during the ongoing refactor.
"""

from __future__ import annotations

import json
import logging
import os
import socket
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Optional

logger = logging.getLogger(__name__)

try:
    # Prefer the consolidated implementation; import the uniquely named
    # module to avoid collision with `services.connection` packages.
    from blender_mcp.connection_core import (
        BlenderConnection,
        get_blender_connection,
        server_lifespan,
    )
except Exception:
    # If import fails, raise early so the developer can correct environment.
    raise


try:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("BlenderMCP", lifespan=server_lifespan)
except Exception:
    mcp = None

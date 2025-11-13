"""Shim module preserving historical import path `blender_mcp.connection`.

Delegates all real behavior to the structured implementation under
`blender_mcp.services.connection` (facade + network + reassembler).

This keeps existing tests/imports working while aligning with the
project's SOLID separation. No new logic should be added here; extend
the service package instead.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict

from .services.connection import BlenderConnection  # facade with multi-mode support

try:  # prefer canonical core accessor if available
    from .connection_core import get_blender_connection, server_lifespan as _core_lifespan  # type: ignore
except Exception:  # fallback: lightweight lifespan using facade
    get_blender_connection = None  # type: ignore

    @asynccontextmanager
    async def _core_lifespan(server: "Any") -> AsyncIterator[Dict[str, Any]]:
        # Minimal lifespan: nothing to initialize; yield empty state
        yield {}


@asynccontextmanager
async def server_lifespan(server: "Any") -> AsyncIterator[Dict[str, Any]]:  # re-export unified name
    async with _core_lifespan(server) as state:
        yield state


__all__ = ["BlenderConnection", "get_blender_connection", "server_lifespan"]

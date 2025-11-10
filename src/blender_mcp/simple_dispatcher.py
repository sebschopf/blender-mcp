"""Compatibility façade.

This module re-exports the canonical `Dispatcher` implementation from
`blender_mcp.dispatcher` so external code that imports
`blender_mcp.simple_dispatcher` keeps working while we maintain a single
source of truth.
"""

from .dispatcher import Dispatcher, register_default_handlers  # type: ignore

__all__ = ["Dispatcher", "register_default_handlers"]

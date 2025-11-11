"""Compatibility adapters for older dispatcher import paths.

Expose names expected by legacy callers while keeping a single canonical
implementation in `dispatchers.dispatcher`.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .dispatcher import _CommandDispatcherCompat as _CompatImpl


# Re-export the compatibility class under the historical name so imports like
# `from blender_mcp.dispatchers import CommandDispatcher` or direct imports
# from older modules continue to work without behavior change.
class CommandDispatcher(_CompatImpl):
    """Thin alias of the internal compatibility dispatcher.

    This class intentionally does not change behavior; it exists so we can
    centralize the implementation in `dispatchers.dispatcher` while keeping
    the surface expected by legacy code.
    """

    pass


__all__ = ["CommandDispatcher"]

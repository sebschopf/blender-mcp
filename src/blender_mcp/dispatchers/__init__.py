"""Dispatchers package public surface.

This module provides a small, explicit API for the `dispatchers` package
and centralizes re-exports so callers can use `from
blender_mcp.dispatchers import Dispatcher`.
"""

from .command_dispatcher import CommandDispatcher as CommandDispatcherImpl
from .dispatcher import (
    Dispatcher,
    HandlerError,
    HandlerNotFound,
    register_default_handlers,
    run_bridge,
)

# Compatibility: also export the compatibility class under the historical
# name from the `compat` module to centralize any future changes.
try:
    from .compat import CommandDispatcher as CommandDispatcherCompat  # type: ignore
except Exception:
    CommandDispatcherCompat = CommandDispatcherImpl

# Maintain the historical name at package level
CommandDispatcher = CommandDispatcherCompat

__all__ = [
    "Dispatcher",
    "register_default_handlers",
    "CommandDispatcher",
    "HandlerError",
    "HandlerNotFound",
    "run_bridge",
]

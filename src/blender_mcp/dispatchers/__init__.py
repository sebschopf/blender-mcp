"""Dispatchers package public surface.

This module provides a small, explicit API for the `dispatchers` package
and centralizes re-exports so callers can use `from
blender_mcp.dispatchers import Dispatcher`.
"""

from .dispatcher import (
    Dispatcher,
    register_default_handlers,
    HandlerError,
    HandlerNotFound,
    run_bridge,
)
from .command_dispatcher import CommandDispatcher as CommandDispatcherImpl

# Maintain the historical name at package level
CommandDispatcher = CommandDispatcherImpl

__all__ = [
    "Dispatcher",
    "register_default_handlers",
    "CommandDispatcher",
    "HandlerError",
    "HandlerNotFound",
    "run_bridge",
]

"""Compatibility façade inside the `dispatchers` package.

This mirrors the previous top-level `simple_dispatcher.py` but points to the
local `dispatcher` implementation inside this package.
"""

from .dispatcher import Dispatcher, register_default_handlers  # type: ignore

__all__ = ["Dispatcher", "register_default_handlers"]

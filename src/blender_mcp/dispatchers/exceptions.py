"""Dispatcher-specific exception types.

Extracted from `dispatcher.py` to keep error types self-contained and
reusable by other modules.
"""
from __future__ import annotations

from typing import Any


class HandlerNotFound(Exception):
    """Raised when a dispatch target cannot be found."""


class HandlerError(Exception):
    """Wraps exceptions raised by handlers.

    Attributes:
        name: the handler name that raised
        original: the original exception instance
    """

    def __init__(self, name: str, original: Exception) -> None:
        super().__init__(f"Handler '{name}' raised {original!r}")
        self.name = name
        self.original = original


__all__ = ["HandlerNotFound", "HandlerError"]

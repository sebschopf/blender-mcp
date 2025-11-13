"""Handler resolution strategy abstraction.

Allows the dispatcher to delegate how a command name is resolved to a callable.
Current default logic preserves existing behavior (registry first, then
service fallback).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:  # Avoid runtime import cycles
    from ..dispatcher import Dispatcher

class HandlerResolutionStrategy:
    def resolve(
        self,
        dispatcher: "Dispatcher",
        name: str,
    ) -> Optional[Callable[[Dict[str, Any]], Any]]:  # pragma: no cover - interface
        raise NotImplementedError


class DefaultHandlerResolutionStrategy(HandlerResolutionStrategy):
    def resolve(
        self,
        dispatcher: "Dispatcher",
        name: str,
    ) -> Optional[Callable[[Dict[str, Any]], Any]]:
        # Use existing dispatcher private method for continuity
        return dispatcher._resolve_handler_or_service(name)

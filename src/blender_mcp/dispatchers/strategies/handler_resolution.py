"""Handler resolution strategy abstraction.

Allows the dispatcher to delegate how a command name is resolved to a callable.
Current default logic preserves existing behavior (registry first, then
service fallback).
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Callable

class HandlerResolutionStrategy:
    def resolve(self, dispatcher: "Dispatcher", name: str) -> Optional[Callable[[Dict[str, Any]], Any]]:  # pragma: no cover - interface
        raise NotImplementedError


class DefaultHandlerResolutionStrategy(HandlerResolutionStrategy):
    def resolve(self, dispatcher: "Dispatcher", name: str) -> Optional[Callable[[Dict[str, Any]], Any]]:
        # Use existing dispatcher private method for continuity
        return dispatcher._resolve_handler_or_service(name)

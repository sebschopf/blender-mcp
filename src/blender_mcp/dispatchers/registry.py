"""HandlerRegistry: separate storage/lookup of handlers from execution.

This small class centralizes handler registration and lookup so the
Dispatcher can focus on execution semantics (error wrapping, timeouts,
etc.). Extracting it makes the registry reusable and testable.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

Handler = Callable[[Dict[str, Any]], Any]


class HandlerRegistry:
    def __init__(self) -> None:
        self._handlers: Dict[str, Handler] = {}

    def register(self, name: str, fn: Handler, *, overwrite: bool = False) -> None:
        if name in self._handlers and not overwrite:
            raise ValueError(f"handler already registered for {name}")
        self._handlers[name] = fn

    def unregister(self, name: str) -> None:
        self._handlers.pop(name, None)

    def list_handlers(self) -> List[str]:
        return sorted(self._handlers.keys())

    def get(self, name: str) -> Optional[Handler]:
        return self._handlers.get(name)

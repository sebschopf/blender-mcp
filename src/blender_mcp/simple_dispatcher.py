"""Tiny dispatcher used by the test shim.

This file is intentionally minimal and import-safe. It provides the
Dispatcher class and a helper to register small default handlers used by
tests (for example `add_primitive`).
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

Handler = Callable[[Dict[str, Any]], Any]


class Dispatcher:
    def __init__(self) -> None:
        self._handlers: Dict[str, Handler] = {}

    def register(self, name: str, fn: Handler) -> None:
        self._handlers[name] = fn

    def unregister(self, name: str) -> None:
        self._handlers.pop(name, None)

    def list_handlers(self) -> List[str]:
        return sorted(self._handlers.keys())

    def dispatch(self, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        fn = self._handlers.get(name)
        if fn is None:
            return None
        return fn(params or {})


def register_default_handlers(dispatcher: Dispatcher) -> None:
    def add_primitive(params: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "primitive": params.get("type", "cube")}

    dispatcher.register("add_primitive", add_primitive)


__all__ = ["Dispatcher", "register_default_handlers"]

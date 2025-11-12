"""Default handler registrations for tests and convenience.

This module contains small helper functions that register a few simple
handlers used by tests and as examples. Extracting these keeps the core
`Dispatcher` focused on handler management.
"""
from __future__ import annotations

from typing import Any, Dict


def register_default_handlers(dispatcher: Any) -> None:
    """Register a couple of minimal handlers useful for tests and defaults."""

    def add_primitive(params: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "primitive": params.get("type", "cube")}

    try:
        dispatcher.register("add_primitive", add_primitive, overwrite=True)  # type: ignore[arg-type]
    except TypeError:
        dispatcher.register("add_primitive", add_primitive)

    def create_dice(params: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "primitive": "dice", "sides": params.get("sides", 6)}

    try:
        dispatcher.register("create_dice", create_dice, overwrite=True)  # type: ignore[arg-type]
    except TypeError:
        dispatcher.register("create_dice", create_dice)


__all__ = ["register_default_handlers"]

"""Façade publique minimale pour le dispatcher.

Expose `Dispatcher` via `blender_mcp.dispatcher` tout en déléguant à
`blender_mcp.dispatchers.dispatcher`. Permet d'ajouter plus tard des
cross-cutting concerns (metrics, audit) sans casser l'implémentation
interne.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .dispatchers.dispatcher import Dispatcher as _InnerDispatcher
from .dispatchers.dispatcher import register_default_handlers as _inner_register_default_handlers

__all__ = ["Dispatcher", "register_default_handlers", "create_dispatcher", "dispatch"]


class Dispatcher(_InnerDispatcher):
    pass  # Pas de logique additionnelle pour l'instant


def register_default_handlers(dispatcher: Dispatcher) -> None:  # pragma: no cover
    _inner_register_default_handlers(dispatcher)


def create_dispatcher() -> Dispatcher:
    return Dispatcher()


def dispatch(dispatcher: Dispatcher, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
    return dispatcher.dispatch(name, params)

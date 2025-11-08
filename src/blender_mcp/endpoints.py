"""Register built-in endpoints (thin wrappers around services).

This module keeps the mapping between endpoint names and service
functions in one place so it's easy to audit which endpoints have been
ported. Handlers are simple callables that accept a `params` dict and
return JSON-serializable results (the services already follow this
convention).
"""
from __future__ import annotations

from typing import Callable

from . import services


def register_builtin_endpoints(register: Callable[[str, Callable], None]) -> None:
    """Register a set of builtin endpoints using the provided `register` function.

    The `register` callable is expected to accept (name, fn) like
    `Dispatcher.register`.
    """

    # thin wrappers in case we need to adapt params in future
    def _execute(params):
        return services.execute_blender_code(params)

    def _scene(params):
        return services.get_scene_info(params)

    def _screenshot(params):
        return services.get_viewport_screenshot(params)

    register("execute_blender_code", _execute)
    register("get_scene_info", _scene)
    register("get_viewport_screenshot", _screenshot)


__all__ = ["register_builtin_endpoints"]

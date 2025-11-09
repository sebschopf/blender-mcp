"""Register built-in endpoints (thin wrappers around services).

This module keeps the mapping between endpoint names and service
functions in one place so it's easy to audit which endpoints have been
ported. Handlers are simple callables that accept a `params` dict and
return JSON-serializable results (the services already follow this
convention).
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from .services.execute import execute_blender_code
from .services.scene import get_scene_info
from .services.screenshot import get_viewport_screenshot

# Typing aliases for endpoint handlers
# Handlers accept a JSON-like parameter mapping (or None) and return any
# JSON-serializable result. Keeping this broad is pragmatic: services
# currently accept plain dicts constructed from parsed JSON RPC params.
Params = Dict[str, Any]
Handler = Callable[[Params], Any]


def register_builtin_endpoints(register: Callable[[str, Handler], None]) -> None:
    """Register a set of builtin endpoints using the provided `register` function.

    The `register` callable is expected to accept (name, fn) like
    `Dispatcher.register`.
    """

    # thin wrappers in case we need to adapt params in future
    def _execute(params: Params) -> Any:
        return execute_blender_code(params)

    def _scene(params: Params) -> Any:
        return get_scene_info(params)

    def _screenshot(params: Params) -> Any:
        return get_viewport_screenshot(params)

    register("execute_blender_code", _execute)
    register("get_scene_info", _scene)
    register("get_viewport_screenshot", _screenshot)


__all__ = ["register_builtin_endpoints"]

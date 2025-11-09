"""Register built-in endpoints (thin wrappers around services).

This module keeps the mapping between endpoint names and service
functions in one place so it's easy to audit which endpoints have been
ported. Handlers are simple callables that accept a `params` dict and
return JSON-serializable results (the services already follow this
convention).
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from .addon_handlers import get_scene_info, get_viewport_screenshot
from .services.execute import execute_blender_code

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
        # delegate to the compatibility façade (no params expected by the
        # refactored implementation) — keep the endpoint signature stable.
        return get_scene_info()

    def _screenshot(params: Params) -> Any:
        # The refactored get_viewport_screenshot accepts explicit args.
        # Map the incoming params dict to the new signature for backward
        # compatibility.
        if isinstance(params, dict):
            max_size = int(params.get("max_size", 800))
            filepath = params.get("filepath")
            fmt = params.get("format", "png")
        else:
            max_size = 800
            filepath = None
            fmt = "png"
        return get_viewport_screenshot(max_size=max_size, filepath=filepath, format=fmt)

    register("execute_blender_code", _execute)
    register("get_scene_info", _scene)
    register("get_viewport_screenshot", _screenshot)

    # small example endpoint useful for health checks and tests
    def _ping(params: Params) -> Dict[str, Any]:
        # echo an optional message provided by callers
        msg = None
        if isinstance(params, dict):
            msg = params.get("msg")
        return {"ok": True, "ping": msg or "pong"}

    register("ping", _ping)


__all__ = ["register_builtin_endpoints"]

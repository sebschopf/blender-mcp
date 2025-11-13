from __future__ import annotations

from blender_mcp.dispatchers.dispatcher import Dispatcher
from blender_mcp.services import registry


def test_dispatcher_fallback_maps_kwargs() -> None:
    # Service qui attend plusieurs kwargs; le dispatcher doit mapper depuis params
    def combine(a: int, b: str) -> str:
        return f"{a}-{b}"

    registry.register_service("_combine_test_service", combine)

    d = Dispatcher()
    res = d.dispatch("_combine_test_service", {"a": 3, "b": "x"})
    assert res == "3-x"


essential_services = [
    "get_scene_info",
    "get_object_info",
    "get_viewport_screenshot",
    "execute_blender_code",
]


def test_registry_lists_core_services() -> None:
    listed = registry.list_services()
    for name in essential_services:
        assert name in listed

import sys
import types

from blender_mcp.dispatchers.dispatcher import Dispatcher
from blender_mcp.endpoints import register_builtin_endpoints


def test_endpoints_registered_and_callable(monkeypatch):
    d = Dispatcher()
    # register builtin endpoints on this dispatcher
    register_builtin_endpoints(d.register)

    # ensure handlers are present
    names = d.list_handlers()
    assert "execute_blender_code" in names
    assert "get_scene_info" in names
    assert "get_viewport_screenshot" in names
    assert "ping" in names

    # mock bpy for scene and screenshot
    fake_bpy = types.SimpleNamespace()
    # minimal scene
    fake_scene = types.SimpleNamespace()
    fake_scene.name = "EScene"
    fake_bpy.context = types.SimpleNamespace(scene=fake_scene)

    class Obj:
        def __init__(self, name, type_):
            self.name = name
            self.type = type_

    fake_bpy.data = types.SimpleNamespace(objects=[Obj("Cube", "MESH")])

    # screenshot helper
    def fake_capture():
        return b"\x89PNG..."

    fake_bpy.capture_viewport_bytes = fake_capture

    sys.modules["bpy"] = fake_bpy
    try:
        # call scene endpoint
        resp_scene = d.dispatch_command({"type": "get_scene_info"})
        assert resp_scene["status"] == "success"

        # call screenshot endpoint
        resp_shot = d.dispatch_command({"type": "get_viewport_screenshot"})
        assert resp_shot["status"] == "success"

        # call ping endpoint with params
        resp_ping = d.dispatch_command({"type": "ping", "params": {"msg": "hello"}})
        assert resp_ping["status"] == "success"
        assert resp_ping["result"]["ping"] == "hello"

    finally:
        del sys.modules["bpy"]

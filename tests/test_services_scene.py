import sys
import types

from blender_mcp.services.scene import get_scene_info


def make_fake_bpy():
    # minimal fake bpy structure: bpy.context.scene.name and bpy.data.objects
    fake = types.SimpleNamespace()
    fake_scene = types.SimpleNamespace()
    fake_scene.name = "TestScene"
    fake_context = types.SimpleNamespace(scene=fake_scene)

    # objects container
    class Obj:
        def __init__(self, name, type_):
            self.name = name
            self.type = type_

    fake_data = types.SimpleNamespace(objects=[Obj("Cube", "MESH"), Obj("Cam", "CAMERA")])

    fake.context = fake_context
    fake.data = fake_data
    return fake


def test_get_scene_info_with_bpy(monkeypatch):
    fake = make_fake_bpy()
    sys.modules["bpy"] = fake
    try:
        resp = get_scene_info()
        assert resp["status"] == "success"
        assert resp["scene_name"] == "TestScene"
        assert any(o["name"] == "Cube" for o in resp["objects"])
    finally:
        del sys.modules["bpy"]


def test_get_scene_info_no_bpy():
    if "bpy" in sys.modules:
        del sys.modules["bpy"]
    resp = get_scene_info()
    assert resp["status"] == "error"

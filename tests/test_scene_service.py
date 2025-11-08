import importlib
import sys
import types

from blender_mcp.services import scene


def test_get_scene_info_no_bpy(monkeypatch):
    # Ensure bpy is not importable
    monkeypatch.setitem(sys.modules, "bpy", None)
    # importlib.import_module will raise when module is None in sys.modules,
    # so remove key entirely
    monkeypatch.delitem(sys.modules, "bpy", raising=False)

    res = scene.get_scene_info()
    assert isinstance(res, dict)
    assert res.get("status") == "error"
    assert "Blender (bpy) not available" in res.get("message", "")


def _make_fake_bpy():
    mod = types.ModuleType("bpy")

    class FakeObj:
        def __init__(self, name, typ):
            self.name = name
            self.type = typ

    mod.data = types.SimpleNamespace(objects=[FakeObj("Cube", "MESH"), FakeObj("Light", "LIGHT")])

    fake_scene = types.SimpleNamespace(
        scene=types.SimpleNamespace(
            name="TestScene",
            camera=types.SimpleNamespace(name="Cam"),
        )
    )
    mod.context = fake_scene

    return mod


def test_get_scene_info_with_bpy(monkeypatch):
    fake = _make_fake_bpy()
    monkeypatch.setitem(sys.modules, "bpy", fake)
    # reload module to ensure it picks up the fake bpy via importlib
    importlib.reload(scene)

    res = scene.get_scene_info()
    assert res.get("status") == "success"
    assert res.get("scene_name") == "TestScene"
    assert isinstance(res.get("objects"), list)
    assert any(o["name"] == "Cube" for o in res.get("objects"))

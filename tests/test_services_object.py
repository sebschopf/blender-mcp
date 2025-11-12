import importlib
import sys
import types

import pytest

from blender_mcp.errors import ExternalServiceError
from blender_mcp.services import object as svc_object


def test_get_object_info_no_bpy(monkeypatch):
    # Ensure bpy is not importable
    monkeypatch.delitem(sys.modules, "bpy", raising=False)
    importlib.reload(svc_object)

    with pytest.raises(ExternalServiceError):
        svc_object.get_object_info({"name": "Cube"})


def _make_fake_bpy():
    mod = types.ModuleType("bpy")

    class FakeObj:
        def __init__(self, name, typ):
            self.name = name
            self.type = typ
            self.location = types.SimpleNamespace(x=0.0, y=0.0, z=0.0)
            self.rotation_euler = types.SimpleNamespace(x=0.0, y=0.0, z=0.0)
            self.scale = types.SimpleNamespace(x=1.0, y=1.0, z=1.0)
            self.visible_get = lambda: True
            self.material_slots = []

    class FakeObjects:
        def __init__(self, items):
            self._items = list(items)

        def get(self, name, default=None):
            for it in self._items:
                if getattr(it, "name", None) == name:
                    return it
            return default

        def __iter__(self):
            return iter(self._items)

        def __len__(self):
            return len(self._items)

    mod.data = types.SimpleNamespace(objects=FakeObjects([FakeObj("Cube", "MESH")]))
    fake_scene = types.SimpleNamespace(
        scene=types.SimpleNamespace(
            name="TestScene",
            objects=[FakeObj("Cube", "MESH")],
        )
    )
    mod.context = fake_scene
    return mod


def test_get_object_info_with_bpy(monkeypatch):
    fake = _make_fake_bpy()
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(svc_object)

    res = svc_object.get_object_info({"name": "Cube"})
    assert res.get("status") == "success"
    assert isinstance(res.get("object"), dict)
    assert res["object"].get("name") == "Cube"

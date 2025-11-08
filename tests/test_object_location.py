import importlib
import sys
import types

from blender_mcp.services import object as object_service


class _Simple:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def _make_fake_bpy_with_obj(location):
    fake = types.ModuleType("bpy")
    o = types.SimpleNamespace()
    o.name = "Lobj"
    o.type = "MESH"
    o.location = location
    fake.data = types.SimpleNamespace(objects=[o])
    return fake


def test_location_attribute_style(monkeypatch):
    fake = _make_fake_bpy_with_obj(_Simple(x=1, y=2, z=3))
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(object_service)

    res = object_service.get_object_info({"name": "Lobj"})
    assert res["status"] == "success"
    assert res["object"]["location"] == [1.0, 2.0, 3.0]


def test_location_sequence(monkeypatch):
    fake = _make_fake_bpy_with_obj([4, "5", 6.0])
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(object_service)

    res = object_service.get_object_info({"name": "Lobj"})
    assert res["status"] == "success"
    assert res["object"]["location"] == [4.0, 5.0, 6.0]


def test_location_short_sequence(monkeypatch):
    fake = _make_fake_bpy_with_obj((7, 8))
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(object_service)

    res = object_service.get_object_info({"name": "Lobj"})
    assert res["status"] == "success"
    # short sequence should NOT be accepted now (we require exactly 3 components)
    assert "location" not in res["object"]


def test_location_mapping_like(monkeypatch):
    fake = _make_fake_bpy_with_obj({"x": 9, "y": "10", "z": 11})
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(object_service)

    res = object_service.get_object_info({"name": "Lobj"})
    assert res["status"] == "success"
    assert res["object"]["location"] == [9.0, 10.0, 11.0]


def test_location_unparseable(monkeypatch):
    class BadLoc:
        pass

    fake = _make_fake_bpy_with_obj(BadLoc())
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(object_service)

    res = object_service.get_object_info({"name": "Lobj"})
    assert res["status"] == "success"
    assert "location" not in res["object"]

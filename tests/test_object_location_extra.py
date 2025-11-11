import array
import importlib
import sys
import types
from decimal import Decimal

from blender_mcp.services import object as object_service


def _make_fake_bpy_with_obj(location):
    fake = types.ModuleType("bpy")
    o = types.SimpleNamespace()
    o.name = "Eobj"
    o.type = "MESH"
    o.location = location
    fake.data = types.SimpleNamespace(objects=[o])
    return fake


def test_location_decimal(monkeypatch):
    fake = _make_fake_bpy_with_obj(types.SimpleNamespace(x=Decimal("1.1"), y=Decimal("2.2"), z=Decimal("3.3")))
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(object_service)

    res = object_service.get_object_info({"name": "Eobj"})
    assert res["status"] == "success"
    assert res["object"]["location"] == [1.1, 2.2, 3.3]


def test_location_array_sequence(monkeypatch):
    arr = array.array("d", [4.0, 5.0, 6.0])
    fake = _make_fake_bpy_with_obj(arr)
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(object_service)

    res = object_service.get_object_info({"name": "Eobj"})
    assert res["status"] == "success"
    assert res["object"]["location"] == [4.0, 5.0, 6.0]


def test_location_non_numeric(monkeypatch):
    fake = _make_fake_bpy_with_obj(types.SimpleNamespace(x="a", y="b", z="c"))
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(object_service)

    res = object_service.get_object_info({"name": "Eobj"})
    assert res["status"] == "success"
    # non-numeric values should not be parsed
    assert "location" not in res["object"]

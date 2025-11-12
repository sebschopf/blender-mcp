import importlib
import sys
import types

import pytest

from blender_mcp.services import object as obj_service
from blender_mcp.errors import InvalidParamsError, ExternalServiceError, HandlerError


def test_get_object_info_missing_name():
    try:
        obj_service.get_object_info({})
        assert False, "expected InvalidParamsError"
    except InvalidParamsError:
        pass


def test_get_object_info_no_bpy(monkeypatch):
    monkeypatch.delitem(sys.modules, "bpy", raising=False)
    importlib.reload(obj_service)
    with pytest.raises(ExternalServiceError):
        obj_service.get_object_info({"name": "Cube"})


def _make_fake_obj(name, typ, loc=None):
    o = types.SimpleNamespace()
    o.name = name
    o.type = typ
    o.location = loc
    return o


def test_get_object_info_found_in_data(monkeypatch):
    fake = types.ModuleType("bpy")
    fake.data = types.SimpleNamespace(objects=[_make_fake_obj("Cube", "MESH"), _make_fake_obj("Lamp", "LIGHT")])
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(obj_service)

    res = obj_service.get_object_info({"name": "Cube"})
    assert res.get("status") == "success"
    assert res.get("object", {}).get("name") == "Cube"


def test_get_object_info_found_in_scene(monkeypatch):
    fake = types.ModuleType("bpy")
    fake.data = types.SimpleNamespace(objects=[])
    fake.context = types.SimpleNamespace(scene=types.SimpleNamespace(objects=[_make_fake_obj("Ball", "MESH")]))
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(obj_service)

    res = obj_service.get_object_info({"name": "Ball"})
    assert res.get("status") == "success"
    assert res.get("object", {}).get("name") == "Ball"


def test_get_object_info_not_found(monkeypatch):
    fake = types.ModuleType("bpy")
    fake.data = types.SimpleNamespace(objects=[_make_fake_obj("Cube", "MESH")])
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(obj_service)
    import pytest

    with pytest.raises(HandlerError) as excinfo:
        obj_service.get_object_info({"name": "DoesNotExist"})
    assert "not found" in str(excinfo.value.original)

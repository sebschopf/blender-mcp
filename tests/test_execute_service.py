import importlib
import sys
import types

from blender_mcp.services import execute


def test_execute_blender_code_missing_param():
    res = execute.execute_blender_code({})
    assert isinstance(res, dict)
    assert res.get("status") == "error"


def test_execute_blender_code_no_bpy(monkeypatch):
    # Ensure bpy is not importable
    monkeypatch.delitem(sys.modules, "bpy", raising=False)
    importlib.reload(execute)
    res = execute.execute_blender_code({"code": "result = 1 + 1"})
    assert res.get("status") == "error"
    assert "Blender (bpy) not available" in res.get("message", "")


def _make_fake_bpy_for_exec():
    # we don't need real bpy API for this test, exec will receive the module
    return types.ModuleType("bpy")


def test_execute_blender_code_success(monkeypatch):
    fake = _make_fake_bpy_for_exec()
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(execute)

    code = "result = 'ok'"
    res = execute.execute_blender_code({"code": code})
    assert res.get("status") == "success"
    assert res.get("result") == "ok"


def test_execute_blender_code_exception(monkeypatch):
    fake = _make_fake_bpy_for_exec()
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(execute)

    code = "raise ValueError('boom')"
    res = execute.execute_blender_code({"code": code})
    assert res.get("status") == "error"
    assert "boom" in res.get("message", "")

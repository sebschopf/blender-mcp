import importlib
import sys
import types

import pytest

from blender_mcp.errors import ExternalServiceError, HandlerError, InvalidParamsError
from blender_mcp.services import execute


def test_execute_blender_code_missing_param():
    try:
        execute.execute_blender_code({})
        assert False, "expected InvalidParamsError"
    except InvalidParamsError:
        pass


def test_execute_blender_code_no_bpy(monkeypatch):
    # Ensure bpy is not importable
    monkeypatch.delitem(sys.modules, "bpy", raising=False)
    importlib.reload(execute)
    with pytest.raises(ExternalServiceError):
        execute.execute_blender_code({"code": "result = 1 + 1"})
    # ExternalServiceError raised as expected; message asserted via exception type


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
    with pytest.raises(HandlerError) as excinfo:
        execute.execute_blender_code({"code": code})
    assert "boom" in str(excinfo.value.original)


def test_execute_blender_code_dry_run(monkeypatch):
    # Provide fake bpy so availability check passes
    fake = _make_fake_bpy_for_exec()
    monkeypatch.setitem(sys.modules, "bpy", fake)
    monkeypatch.setenv("BLENDER_MCP_EXECUTE_DRY_RUN", "1")
    importlib.reload(execute)

    code = "result = 'should_not_run'"  # result should not be set in dry-run
    res = execute.execute_blender_code({"code": code})
    assert res.get("status") == "ok"
    assert "dry-run" in res.get("message", "")

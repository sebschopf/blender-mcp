from __future__ import annotations

from typing import Any, Dict

from blender_mcp.types import DispatcherResult, ToolCommand, ToolInfo


def test_dispatcher_result_success_shape() -> None:
    res: DispatcherResult = {"status": "success", "result": {"value": 1}}
    assert res["status"] == "success"
    assert isinstance(res["result"], dict)


def test_dispatcher_result_error_shape() -> None:
    err: DispatcherResult = {
        "status": "error",
        "message": "boom",
        "error_code": "internal_error",
    }
    assert err["status"] == "error"
    assert "message" in err and "error_code" in err


def test_tool_command_variants() -> None:
    c1: ToolCommand = {"tool": "execute_script", "params": {"code": "print(1)"}}
    c2: ToolCommand = {"clarify": ["which object?"]}
    assert c1.get("tool") == "execute_script"
    assert isinstance(c1.get("params"), dict)
    assert c2.get("clarify") == ["which object?"]


def test_tool_info_partial() -> None:
    info: ToolInfo = {"name": "execute_script", "doc": "Run arbitrary code."}
    assert info["name"] == "execute_script"
    assert "doc" in info

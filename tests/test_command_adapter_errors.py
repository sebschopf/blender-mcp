from typing import Any, Dict

from blender_mcp.dispatchers.command_adapter import CommandAdapter
from blender_mcp.errors import InvalidParamsError


class FakeDispatcher:
    def __init__(self, behavior: str):
        self.behavior = behavior

    def list_handlers(self):
        return ["do_thing"]

    def dispatch(self, name: str, params: Dict[str, Any]):
        if self.behavior == "invalid":
            raise InvalidParamsError("missing field 'foo'")
        if self.behavior == "boom":
            raise RuntimeError("unexpected")
        return {"ok": True, "handled": name}


def test_adapter_maps_invalid_params_to_error_code():
    adapter = CommandAdapter(FakeDispatcher("invalid"))
    res = adapter.dispatch_command({"type": "do_thing", "params": {}})
    assert res["status"] == "error"
    assert res.get("error_code") == "invalid_params"
    assert "missing field" in res["message"]


def test_adapter_unknown_command_returns_not_found():
    adapter = CommandAdapter(FakeDispatcher("ok"))
    res = adapter.dispatch_command({"type": "unknown_cmd", "params": {}})
    assert res["status"] == "error"
    assert res.get("error_code") == "not_found"


def test_adapter_success_path_preserved():
    adapter = CommandAdapter(FakeDispatcher("ok"))
    res = adapter.dispatch_command({"type": "do_thing", "params": {}})
    assert res["status"] == "success"
    assert res["result"] == {"ok": True, "handled": "do_thing"}

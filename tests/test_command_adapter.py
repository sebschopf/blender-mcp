from __future__ import annotations

from blender_mcp.dispatchers.command_adapter import CommandAdapter
from blender_mcp.dispatchers.dispatcher import Dispatcher


def test_command_adapter_success_and_unknown() -> None:
    d = Dispatcher()

    def ok_handler(params):
        return {"n": params.get("n", 0)}

    d.register("ok", ok_handler, overwrite=True)

    adapter = CommandAdapter(d)
    resp = adapter.dispatch_command({"type": "ok", "params": {"n": 3}})
    assert resp["status"] == "success"
    assert resp["result"] == {"n": 3}

    resp2 = adapter.dispatch_command({"type": "missing", "params": {}})
    assert resp2["status"] == "error"


def test_command_adapter_invalid_format_and_handler_error() -> None:
    d = Dispatcher()

    def err_handler(_params):
        raise RuntimeError("boom")

    d.register("err", err_handler, overwrite=True)

    adapter = CommandAdapter(d)
    bad = adapter.dispatch_command("not a dict")
    assert bad["status"] == "error"

    resp = adapter.dispatch_command({"type": "err", "params": {}})
    assert resp["status"] == "error"
    assert "boom" in resp["message"]

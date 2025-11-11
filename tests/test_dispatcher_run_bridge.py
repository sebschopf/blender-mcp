import builtins
import importlib
from typing import Any, Dict

import pytest

dispatcher = importlib.import_module("blender_mcp.dispatchers.dispatcher")
from blender_mcp.dispatchers.dispatcher import Dispatcher, _CommandDispatcherCompat


def test_run_bridge_calls_local_handler(monkeypatch):
    calls: Dict[str, Any] = {}

    # mock gemini to return a tool mapping
    def fake_gemini(_prompt: str, use_api: bool = False):
        return {"tool": "create_dice", "params": {"sides": 8}}

    monkeypatch.setattr(dispatcher, "call_gemini_cli", fake_gemini)

    # create a compat dispatcher and register a handler that records the call
    compat = _CommandDispatcherCompat()

    def handler(params, config=None):
        calls["handler_called_with"] = dict(params or {})
        calls["config"] = config
        return {"ok": True}

    compat.register("create_dice", handler)

    # monkeypatch call_mcp_tool so it's obvious if it's used
    def fake_mcp(tool: str, params: Dict[str, Any]):
        calls["mcp_called"] = (tool, params)

    monkeypatch.setattr(dispatcher, "call_mcp_tool", fake_mcp)

    # Run the bridge; should call local handler, not remote
    dispatcher.run_bridge("make dice", config={"user": "test"}, dispatcher=compat, use_api=False)

    assert "handler_called_with" in calls
    assert calls["handler_called_with"].get("sides") == 8
    assert "mcp_called" not in calls


def test_run_bridge_handles_clarify_loop(monkeypatch):
    # This simulates Gemini asking to clarify and then returning a tool mapping.
    seq = [
        {"clarify": ["Which sides?"]},
        {"tool": "create_dice", "params": {"sides": 12}},
    ]

    def fake_gemini(prompt: str, use_api: bool = False):
        # pop from sequence
        return seq.pop(0)

    monkeypatch.setattr(dispatcher, "call_gemini_cli", fake_gemini)

    compat = _CommandDispatcherCompat()

    def handler(params, config=None):
        return {"result": params}

    compat.register("create_dice", handler)

    # Monkeypatch builtins.input so the clarify prompt loop provides an answer
    monkeypatch.setattr(builtins, "input", lambda p: "12")

    # Now run; should eventually call handler and return
    dispatcher.run_bridge("make dice", config=None, dispatcher=compat, use_api=False)

    # If no exception raised, the flow succeeded.
    assert True


def test_dispatch_with_timeout_times_out():
    d = Dispatcher()

    def long_running(params):
        import time

        time.sleep(0.2)
        return "done"

    d.register("long", long_running)

    with pytest.raises(TimeoutError):
        # use a very small timeout
        d.dispatch_with_timeout("long", params={}, timeout=0.01)


def test_dispatch_command_error_and_success():
    d = Dispatcher()

    def ok_handler(p):
        return {"x": 1}

    d.register("ok", ok_handler)

    res = d.dispatch_command({"type": "ok", "params": {}})
    assert res["status"] == "success"
    assert res["result"]["x"] == 1

    res2 = d.dispatch_command({"type": "missing", "params": {}})
    assert res2["status"] == "error"

    # invalid command format
    res3 = d.dispatch_command("not a dict")
    assert res3["status"] == "error"

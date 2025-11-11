import builtins

import pytest

import blender_mcp.dispatchers.dispatcher as dispatcher
from blender_mcp.config import BridgeConfig
from blender_mcp.dispatchers.dispatcher import (
    CommandDispatcher,
    Dispatcher,
    HandlerError,
    run_bridge,
)
from blender_mcp.dispatchers.dispatcher import (
    register_default_handlers as register_default_handlers_cmd,
)
from blender_mcp.server_shim import BlenderMCPServer
from blender_mcp.simple_dispatcher import (
    Dispatcher as SimpleDispatcher,
)
from blender_mcp.simple_dispatcher import (
    register_default_handlers as simple_register_default_handlers,
)


def test_register_and_dispatch():
    d = Dispatcher()

    def add(params):
        return params.get("a", 0) + params.get("b", 0)

    d.register("add", add, overwrite=True)

    handlers = d.list_handlers()
    assert "add" in handlers
    assert d.dispatch("add", {"a": 2, "b": 3}) == 5


def test_unknown_handler_returns_none():
    d = Dispatcher()
    # The Dispatcher.dispatch returns None when a handler is missing
    assert d.dispatch("does-not-exist") is None


def test_handler_exception_wrapped():
    d = Dispatcher()

    def fail(params):
        raise ValueError("boom")

    d.register("bad", fail, overwrite=True)
    with pytest.raises(HandlerError) as excinfo:
        d.dispatch("bad", {})

    assert isinstance(excinfo.value.original, ValueError)
    assert "bad" in str(excinfo.value)


def test_dispatcher_register_and_dispatch():
    d = SimpleDispatcher()
    assert d.list_handlers() == []

    d.register("t1", lambda params: {"r": params.get("x", 0)})
    assert "t1" in d.list_handlers()
    assert d.dispatch("t1", {"x": 5}) == {"r": 5}
    assert d.dispatch("missing") is None


def test_register_default_handlers_and_server_integration():
    d = SimpleDispatcher()
    simple_register_default_handlers(d)
    assert "add_primitive" in d.list_handlers()

    s = BlenderMCPServer()
    # ensure server uses dispatcher and default handler
    resp = s.execute_command({"tool": "add_primitive", "params": {"type": "sphere"}})
    assert resp["status"] == "ok"
    assert resp.get("handled") is True
    assert resp["result"]["primitive"] == "sphere"


def test_register_and_dispatch_commanddispatcher():
    disp = CommandDispatcher()

    def handler(params, config):
        return {"ok": True, "received": params}

    disp.register("foo", handler)
    res = disp.dispatch("foo", {"x": 1}, None)
    assert res["ok"] is True
    assert res["received"] == {"x": 1}


def test_unregister_and_missing():
    disp = CommandDispatcher()

    def handler(*a, **k):
        return None

    disp.register("bar", handler)
    disp.unregister("bar")
    with pytest.raises(KeyError):
        disp.dispatch("bar")


def test_register_default_handlers():
    disp = CommandDispatcher()
    register_default_handlers_cmd(disp)
    # ensure core names are registered
    assert "add_primitive" in disp.list_handlers()
    assert "create_dice" in disp.list_handlers()


def test_run_bridge_calls_primitive_handler(monkeypatch):
    cfg = BridgeConfig()

    # Gemini returns a mapping to add_primitive
    def fake_gemini(_user_req, use_api=False):
        return {"tool": "add_primitive", "params": {"type": "cube", "size": 2}}

    called = {}

    def fake_handle(params, config):
        called["params"] = params
        called["config"] = config
        return {"ok": True}

    # Replace the gemini client used by the dispatcher module
    monkeypatch.setattr(dispatcher, "call_gemini_cli", fake_gemini)

    # Create a dispatcher and register our fake handler, then pass it to run_bridge
    disp = CommandDispatcher()
    disp.register("add_primitive", fake_handle)

    run_bridge("make a cube", cfg, disp, use_api=False)

    assert called["params"] == {"type": "cube", "size": 2}
    assert called["config"] is cfg


def test_run_bridge_clarify_then_mapped(monkeypatch):
    cfg = BridgeConfig()

    # First response asks for clarification, second gives a tool mapping
    sequence = [
        {"clarify": ["Quelle taille ?"]},
        {"tool": "add_primitive", "params": {"type": "cube", "size": 3}},
    ]

    def fake_gemini(_user_req, use_api=False):
        return sequence.pop(0)

    called = {}

    def fake_handle(params, config):
        called["params"] = params
        return {"ok": True}

    # Simulate user input when clarification is requested
    monkeypatch.setattr(builtins, "input", lambda prompt="": "size=3")
    monkeypatch.setattr(dispatcher, "call_gemini_cli", fake_gemini)

    disp = CommandDispatcher()
    disp.register("add_primitive", fake_handle)

    run_bridge("please make something", cfg, disp, use_api=False)

    assert called.get("params") == {"type": "cube", "size": 3}


def test_run_bridge_direct_mcp_call(monkeypatch):
    cfg = BridgeConfig()

    def fake_gemini(_user_req, use_api=False):
        return {"tool": "some_mcp_tool", "params": {"foo": "bar"}}

    called = {}

    def fake_call_mcp(tool, params):
        called["tool"] = tool
        called["params"] = params
        return {"result": "ok"}

    monkeypatch.setattr(dispatcher, "call_gemini_cli", fake_gemini)
    monkeypatch.setattr(dispatcher, "call_mcp_tool", fake_call_mcp)

    # Use an empty dispatcher since no mapped handler should be invoked
    disp = CommandDispatcher()
    run_bridge("call an mcp tool", cfg, disp, use_api=False)

    assert called["tool"] == "some_mcp_tool"
    assert called["params"] == {"foo": "bar"}

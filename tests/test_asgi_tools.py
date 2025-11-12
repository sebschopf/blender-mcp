import pytest

pytest.importorskip("fastapi")

import importlib

from fastapi.testclient import TestClient

from blender_mcp import asgi
from blender_mcp.errors import ExecutionTimeoutError, InvalidParamsError

client = TestClient(asgi.app)


def _register_tmp_tool(name: str, func):
    """Helper: attach a tool function to the server module and return a cleanup func."""
    srv = importlib.import_module("blender_mcp.server")
    prev = getattr(srv, name, None)
    setattr(srv, name, func)

    def _cleanup():
        if prev is None:
            try:
                delattr(srv, name)
            except Exception:
                pass
        else:
            setattr(srv, name, prev)

    return _cleanup


def test_call_tool_success(monkeypatch):
    def echo_tool(ctx, **params):
        return {"echo": params}

    cleanup = _register_tmp_tool("echo_tool", echo_tool)
    # spy log_action
    called = {}

    def fake_log_action(source, action, params=None, result=None):
        called["last"] = (source, action, params, result)

    monkeypatch.setattr("blender_mcp.logging_utils.log_action", fake_log_action)

    resp = client.post(
        "/tools/echo_tool", json={"params": {"x": 1, "y": "a"}}
    )
    cleanup()

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["result"]["echo"]["x"] == 1
    # audit called for success
    assert "last" in called
    src, action, params, result = called["last"]
    assert src == "asgi"
    assert action == "call_tool"
    assert params["tool"] == "echo_tool"


def test_call_tool_invalid_params(monkeypatch):
    def bad_tool(ctx, **params):
        raise InvalidParamsError("missing foo")

    cleanup = _register_tmp_tool("bad_tool", bad_tool)
    called = {}

    def fake_log_action(source, action, params=None, result=None):
        called["last"] = (source, action, params, result)

    monkeypatch.setattr("blender_mcp.logging_utils.log_action", fake_log_action)

    resp = client.post("/tools/bad_tool", json={"params": {}})
    cleanup()

    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "error"
    assert body["error_code"] == "invalid_params"
    # audit called for error
    assert "last" in called
    src, action, params, result = called["last"]
    assert action == "call_tool_error"


def test_call_tool_timeout(monkeypatch):
    async def slow_tool(ctx, **params):
        raise ExecutionTimeoutError("timeout")

    cleanup = _register_tmp_tool("slow_tool", slow_tool)
    called = {}

    def fake_log_action(source, action, params=None, result=None):
        called["last"] = (source, action, params, result)

    monkeypatch.setattr("blender_mcp.logging_utils.log_action", fake_log_action)

    resp = client.post("/tools/slow_tool", json={"params": {}})
    cleanup()

    assert resp.status_code == 504
    body = resp.json()
    assert body["status"] == "error"
    assert body["error_code"] == "timeout"
    assert "last" in called
    src, action, params, result = called["last"]
    assert action == "call_tool_error"

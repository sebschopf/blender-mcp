from __future__ import annotations

from blender_mcp import http as http_mod
from blender_mcp import mcp_client


class DummyResponse:
    def __init__(self, payload: object | None = None):
        self._payload = payload or {"ok": True}

    def raise_for_status(self) -> None:
        return None

    def json(self) -> object:
        return self._payload


class DummySession:
    def __init__(self):
        self.last_post = None

    def post(self, url: str, json: object | None = None, timeout: int | None = None):
        # record the call and return a harmless response
        self.last_post = {"url": url, "json": json, "timeout": timeout}
        return DummyResponse({"used_session": True, "url": url})


def test_call_mcp_tool_uses_provided_session():
    dummy = DummySession()
    result = mcp_client.call_mcp_tool("test-tool", {"a": 1}, session=dummy)
    assert result == {"used_session": True, "url": "http://127.0.0.1:8000/tools/test-tool"}
    assert dummy.last_post is not None
    assert dummy.last_post["json"]["params"] == {"a": 1}


def test_call_mcp_tool_uses_global_session_when_none(monkeypatch):
    dummy = DummySession()

    # monkeypatch the get_session reference used by mcp_client
    monkeypatch.setattr(mcp_client, "get_session", lambda: dummy)

    result = mcp_client.call_mcp_tool("global-tool", None, session=None)
    assert result == {"used_session": True, "url": "http://127.0.0.1:8000/tools/global-tool"}
    assert dummy.last_post is not None


def test_reset_session_creates_new_instance():
    # ensure a session exists
    s1 = http_mod.get_session()
    # reset
    http_mod.reset_session()
    s2 = http_mod.get_session()
    assert s1 is not s2

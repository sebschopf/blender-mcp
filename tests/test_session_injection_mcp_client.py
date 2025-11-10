from __future__ import annotations

from typing import Any

from blender_mcp import mcp_client


class _FakeResp:
    def __init__(self, json_data: Any = None, status: int = 200):
        self._json = json_data if json_data is not None else {}
        self.status_code = status

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP {self.status_code}")

    def json(self) -> Any:
        return self._json


class FakeSession:
    def __init__(self):
        self.posts = []

    def post(self, url: str, **kwargs) -> _FakeResp:
        self.posts.append((url, kwargs))
        return _FakeResp(json_data={"result": "ok"}, status=200)


def test_call_mcp_tool_with_session():
    sess = FakeSession()
    res = mcp_client.call_mcp_tool("test-tool", {"x": 1}, session=sess)
    assert res == {"result": "ok"}
    assert len(sess.posts) == 1


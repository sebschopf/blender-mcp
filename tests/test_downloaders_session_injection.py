from __future__ import annotations

from typing import Any, Dict

from blender_mcp import downloaders


class DummyResponse:
    def __init__(self, payload: bytes | None = None, status_code: int = 200):
        self._payload = payload or b"ok"
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if not (200 <= self.status_code < 300):
            raise RuntimeError("HTTP error")

    @property
    def content(self) -> bytes:
        return self._payload


class DummySession:
    def __init__(self):
        self.last_get = None

    def get(self, url: str, timeout: int | None = None, headers: Dict[str, Any] | None = None):
        self.last_get = {"url": url, "timeout": timeout, "headers": headers}
        return DummyResponse(b"dummy-bytes", 200)


def test_download_bytes_uses_provided_session():
    dummy = DummySession()
    out = downloaders.download_bytes("https://example.com/test.bin", timeout=5, session=dummy)
    assert out == b"dummy-bytes"
    assert dummy.last_get is not None
    assert dummy.last_get["url"].endswith("/test.bin")

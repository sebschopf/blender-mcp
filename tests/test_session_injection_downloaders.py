from __future__ import annotations

from typing import Optional, Dict, Any, cast, Any as _Any, Mapping
import requests

from blender_mcp.downloaders import download_bytes
from blender_mcp import downloaders


class FakeResp:
    def __init__(self, content: bytes = b"ok", status: int = 200) -> None:
        self.content: bytes = content
        self.status_code: int = status

    def raise_for_status(self) -> None:
        if 400 <= self.status_code < 600:
            raise Exception("HTTP")


class FakeSession1:
    def __init__(self, resp: FakeResp) -> None:
        self._resp = resp

    def get(self, url: str, timeout: Optional[float] = None, headers: Optional[Dict[str, Any]] = None) -> FakeResp:
        return self._resp


def test_download_bytes_injected_session() -> None:
    fake = FakeSession1(FakeResp(b"hello", status=200))
    # cast to requests.Session for type-checker friendliness in tests
    data = download_bytes("https://example.com/file", session=cast(requests.Session, fake))
    assert data == b"hello"


class _FakeResp:
    def __init__(self, content: bytes = b"ok", status: int = 200):
        self.content = content
        self.status_code = status

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP {self.status_code}")


class FakeSession2:
    def __init__(self):
        self.calls = []

    def get(self, url: str, **kwargs) -> _FakeResp:
        self.calls.append((url, kwargs))
        return _FakeResp(content=b"data-bytes", status=200)


def test_download_bytes_uses_injected_session():
    sess = FakeSession2()
    data = downloaders.download_bytes("https://example.org/file", session=sess)
    assert data == b"data-bytes"
    assert len(sess.calls) == 1


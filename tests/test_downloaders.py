"""Tests for downloaders using monkeypatched requests and an in-memory zip."""

from __future__ import annotations

import io
import zipfile

import pytest

from blender_mcp import downloaders


class DummyResp:
    def __init__(self, content: bytes, status: int = 200):
        self.content = content
        self.status_code = status

    def raise_for_status(self):
        if self.status_code != 200:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_download_bytes_success(monkeypatch):
    called = {}

    def fake_get(url, timeout=None, headers=None):
        assert url == "https://example.com/foo"
        called["ok"] = True
        return DummyResp(b"ok")

    monkeypatch.setattr(downloaders.requests, "get", fake_get)

    data = downloaders.download_bytes("https://example.com/foo", timeout=5)
    assert data == b"ok"
    assert called.get("ok")


def test_download_bytes_raises_on_error(monkeypatch):
    def fake_get(url, timeout=None, headers=None):
        return DummyResp(b"", status=404)

    monkeypatch.setattr(downloaders.requests, "get", fake_get)

    with pytest.raises(RuntimeError):
        downloaders.download_bytes("https://example.com/missing")


def make_zip_bytes(files: dict[str, bytes]) -> bytes:
    buff = io.BytesIO()
    with zipfile.ZipFile(buff, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)
    return buff.getvalue()


def test_secure_extract_zip_bytes_extracts_and_rejects_traversal(tmp_path):
    normal_zip = make_zip_bytes({"a.txt": b"hello", "dir/b.txt": b"bye"})
    target = tmp_path / "out"
    target.mkdir()
    downloaders.secure_extract_zip_bytes(normal_zip, str(target))
    assert (target / "a.txt").exists()
    assert (target / "dir" / "b.txt").exists()

    # Create a zip with a path traversal entry
    traversal_zip = make_zip_bytes({"../evil.txt": b"bad"})
    with pytest.raises(ValueError):
        downloaders.secure_extract_zip_bytes(traversal_zip, str(target))

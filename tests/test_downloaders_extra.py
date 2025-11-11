"""Additional tests for downloaders helpers added during refactor.

Covers download_to_tempfile happy/error paths.
"""

from __future__ import annotations

import os

import pytest

from blender_mcp import downloaders


def test_download_to_tempfile_happy_path(monkeypatch, tmp_path):
    # Monkeypatch download_bytes used by download_to_tempfile
    def fake_download_bytes(url, timeout=None, headers=None):
        assert url == "https://example.com/data.bin"
        return b"HELLO"

    monkeypatch.setattr(downloaders, "download_bytes", fake_download_bytes)

    out = downloaders.download_to_tempfile("https://example.com/data.bin", prefix="p_", suffix=".bin")
    assert os.path.exists(out)
    with open(out, "rb") as fh:
        data = fh.read()
    assert data == b"HELLO"
    os.unlink(out)


def test_download_to_tempfile_propagates_errors(monkeypatch):
    def fake_download_bytes(url, timeout=None, headers=None):
        raise RuntimeError("network fail")

    monkeypatch.setattr(downloaders, "download_bytes", fake_download_bytes)

    with pytest.raises(RuntimeError):
        downloaders.download_to_tempfile("https://example.com/broken")

import os
import sys

TEST_ROOT = os.path.dirname(__file__)
SRC_PATH = os.path.abspath(os.path.join(TEST_ROOT, "..", "src"))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import blender_mcp.sketchfab as sketchfab


class DummyResp:
    def __init__(self, code, data):
        self.status_code = code
        self._data = data

    def json(self):
        return self._data


def test_download_model_fallback_returns_error_when_download_fails(monkeypatch):
    # Mock initial metadata request
    def fake_get_meta(url, headers=None, timeout=None):
        return DummyResp(200, {"gltf": {"url": "https://example.com/model.zip"}})

    monkeypatch.setattr(sketchfab.requests, "get", fake_get_meta)

    # Make downloaders.download_bytes raise to simulate helper failure
    def fake_download_bytes(url, timeout=30):
        raise RuntimeError("no downloader")

    monkeypatch.setattr(sketchfab.downloaders, "download_bytes", fake_download_bytes)

    res = sketchfab.download_model(api_key="tok", uid="u1")
    assert "error" in res

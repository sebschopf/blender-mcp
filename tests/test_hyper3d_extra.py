import os
import sys

TEST_ROOT = os.path.dirname(__file__)
SRC_PATH = os.path.abspath(os.path.join(TEST_ROOT, "..", "src"))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import blender_mcp.hyper3d as hyper3d


class DummyResp:
    def __init__(self, code, data):
        self.status_code = code
        self._data = data

    def json(self):
        return self._data


def test_import_generated_asset_main_site_streaming_fallback(monkeypatch, tmp_path):
    # Simulate the /download endpoint returning a list with a glb URL
    def fake_post(url, headers=None, json=None):
        return DummyResp(200, {"list": [{"name": "asset.glb", "url": "https://example.com/asset.glb"}]})

    monkeypatch.setattr(hyper3d.requests, "post", fake_post)

    # Make downloaders.download_bytes raise so the code falls back to streaming
    def fake_download_bytes(url, timeout=30):
        raise RuntimeError("download helper not available")

    monkeypatch.setattr(hyper3d.downloaders, "download_bytes", fake_download_bytes)

    # Fake requests.get streaming response
    class StreamResp:
        def __init__(self, content: bytes):
            self.status_code = 200
            self._content = content

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            # Yield content in two chunks
            yield self._content[: len(self._content) // 2]
            yield self._content[len(self._content) // 2 :]

    def fake_get(url, stream=None, headers=None, timeout=None):
        return StreamResp(b"GLB-DATA")

    monkeypatch.setattr(hyper3d.requests, "get", fake_get)

    res = hyper3d.import_generated_asset_main_site(api_key="k", task_uuid="t1", name="n")
    assert res.get("succeed") is True
    assert os.path.exists(res.get("temp_file"))


def test_import_generated_asset_fal_ai_prefers_downloaders(monkeypatch, tmp_path):
    # Respond with a model_mesh url
    def fake_get_meta(url, headers=None):
        return DummyResp(200, {"model_mesh": {"url": "https://example.com/m.glb"}})

    monkeypatch.setattr(hyper3d.requests, "get", fake_get_meta)

    called = {}

    def fake_download_bytes(url, timeout=30):
        called["url"] = url
        # write a glb file bytes
        return b"GLB"

    monkeypatch.setattr(hyper3d.downloaders, "download_bytes", fake_download_bytes)

    res = hyper3d.import_generated_asset_fal_ai(api_key="k", request_id="r1", name="nm")
    assert res.get("succeed") is True
    assert "temp_file" in res
    assert called.get("url") is not None


def test_poll_rodin_job_status_fal_ai_fallback(monkeypatch):
    # Simulate helper missing and fallback to requests.get
    def fake_poll(url, headers=None):
        return DummyResp(200, {"status": "done"})

    monkeypatch.setattr(hyper3d.requests, "get", fake_poll)

    res = hyper3d.poll_rodin_job_status_fal_ai(api_key="k", request_id="rid")
    assert isinstance(res, dict)

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


def test_create_rodin_job_main_site(monkeypatch):
    def fake_post(url, headers=None, files=None):
        return DummyResp(200, {"job": "ok"})

    monkeypatch.setattr(hyper3d.requests, "post", fake_post)
    res = hyper3d.create_rodin_job_main_site(api_key="k", text_prompt="hi")
    assert res.get("job") == "ok"


def test_poll_status_main_site(monkeypatch):
    def fake_post(url, headers=None, json=None):
        return DummyResp(200, {"jobs": [{"status": "done"}, {"status": "queued"}]})

    monkeypatch.setattr(hyper3d.requests, "post", fake_post)
    res = hyper3d.poll_rodin_job_status_main_site(api_key="k", subscription_key="s")
    assert res["status_list"] == ["done", "queued"]


def test_import_generated_asset_main_site(monkeypatch, tmp_path):  # noqa: C901
    # Mock the download list
    def fake_post(url, headers=None, json=None):
        return DummyResp(200, {"list": [{"name": "asset.glb", "url": "https://example.com/asset.glb"}]})

    monkeypatch.setattr(hyper3d.requests, "post", fake_post)

    called = {}

    def fake_download_bytes(url, timeout=30):
        called["url"] = url
        return b"GLB"

    monkeypatch.setattr(hyper3d.downloaders, "download_bytes", fake_download_bytes)

    res = hyper3d.import_generated_asset_main_site(api_key="k", task_uuid="t1", name="n")
    assert res.get("succeed") is True
    assert os.path.exists(res.get("temp_file"))

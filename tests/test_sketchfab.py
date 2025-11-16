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


def test_get_sketchfab_status_ok(monkeypatch):
    def fake_get(url, headers=None, timeout=None):
        return DummyResp(200, {"username": "alice"})

    class DummySession:
        def get(self, url, timeout=None, headers=None, params=None, **kwargs):
            return fake_get(url, headers=headers, timeout=timeout)

    monkeypatch.setattr("blender_mcp.http.get_session", lambda: DummySession())
    res = sketchfab.get_sketchfab_status("token-123")
    assert res["enabled"] is True
    assert "alice" in res["message"]


def test_search_models_error_auth(monkeypatch):
    def fake_get(url, headers=None, params=None, timeout=None):
        return DummyResp(401, {})

    class DummySession:
        def get(self, url, timeout=None, headers=None, params=None, **kwargs):
            return fake_get(url, headers=headers, params=params, timeout=timeout)

    monkeypatch.setattr("blender_mcp.http.get_session", lambda: DummySession())
    res = sketchfab.search_models(api_key="bad", query="test")
    assert "error" in res


def test_download_model_uses_downloaders(monkeypatch, tmp_path):
    # Provide a fake downloaders implementation
    called = {}

    def fake_download_bytes(url, timeout=30):
        called["url"] = url
        # Create a small zip file in memory with a dummy glb
        import io
        import zipfile

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("model.glb", b"GLB")
        return buf.getvalue()

    def fake_extract(zip_bytes):
        d = tmp_path / "extracted"
        d.mkdir()
        p = d / "model.glb"
        p.write_bytes(b"GLB")
        return str(d)

    monkeypatch.setattr(sketchfab.downloaders, "download_bytes", fake_download_bytes)
    monkeypatch.setattr(sketchfab.downloaders, "secure_extract_zip_bytes", fake_extract)

    # Mock the initial Sketchfab download metadata request
    def fake_get(url, headers=None, timeout=None):
        return DummyResp(200, {"gltf": {"url": "https://example.com/model.zip"}})

    class DummySession:
        def get(self, url, timeout=None, headers=None, params=None, **kwargs):
            return fake_get(url, headers=headers, timeout=timeout)

    monkeypatch.setattr("blender_mcp.http.get_session", lambda: DummySession())

    res = sketchfab.download_model(api_key="tok", uid="u123")
    assert "temp_dir" in res
    assert called.get("url") is not None

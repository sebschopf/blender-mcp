import io
import zipfile

from blender_mcp.services import sketchfab as services_sketchfab


class DummyResp:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._data


def test_get_sketchfab_status_no_key():
    res = services_sketchfab.get_sketchfab_status(None)
    assert res.get("enabled") is False


def test_search_models_with_key(monkeypatch):
    def fake_get(url, headers=None, params=None, timeout=None):
        assert "search" in url
        return DummyResp(200, {"results": [{"name": "Model1"}]})

    class DummySession:
        def get(self, url, timeout=None, headers=None, params=None, **kwargs):
            return fake_get(url, headers=headers, params=params, timeout=timeout)

    monkeypatch.setattr("blender_mcp.http.get_session", lambda: DummySession())
    data = services_sketchfab.search_models("apikey", "chair", None, count=5, downloadable=True)
    assert "results" in data


def test_download_model_uses_downloaders(monkeypatch, tmp_path):
    # Mock Sketchfab download endpoint returning gltf.url
    def fake_get(url, headers=None, timeout=None):
        if "download" in url:
            return DummyResp(200, {"gltf": {"url": "http://example.com/model.zip"}})
        return DummyResp(404, {})

    # Create a zip bytes
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, mode="w") as z:
        z.writestr("f.txt", "x")
    zip_bytes = bio.getvalue()

    class DummySession:
        def get(self, url, timeout=None, headers=None, params=None, **kwargs):
            return fake_get(url, headers=headers, timeout=timeout)

    monkeypatch.setattr("blender_mcp.http.get_session", lambda: DummySession())
    # Patch downloaders used by the top-level sketchfab module
    from blender_mcp import downloaders

    monkeypatch.setattr(downloaders, "download_bytes", lambda url, timeout=60, headers=None: zip_bytes)
    monkeypatch.setattr(downloaders, "secure_extract_zip_bytes", lambda b: str(tmp_path))

    res = services_sketchfab.download_model("apikey", "uid123")
    assert "temp_dir" in res or "error" not in res

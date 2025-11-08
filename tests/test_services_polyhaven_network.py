import io
import zipfile

from blender_mcp.services import polyhaven


class DummyResp:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._data


def test_fetch_categories_requests(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        assert "list" in url
        return DummyResp(200, {"categories": {"c1": 5}})

    monkeypatch.setattr(polyhaven.requests, "get", fake_get)
    res = polyhaven.fetch_categories(asset_type="textures")
    assert res["categories"]["c1"] == 5


def test_download_asset_uses_downloader(monkeypatch, tmp_path):
    # Create a small zip in memory
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, mode="w") as z:
        z.writestr("file.txt", "hello")
    zip_bytes = bio.getvalue()

    def fake_download_bytes(url, timeout=60, headers=None):
        assert "polyhaven" in url or url.startswith("http")
        return zip_bytes

    def fake_extract(zip_b):
        return str(tmp_path)

    monkeypatch.setattr(polyhaven.downloaders, "download_bytes", fake_download_bytes)
    monkeypatch.setattr(polyhaven.downloaders, "secure_extract_zip_bytes", lambda b: fake_extract(b))

    result = polyhaven.download_asset(download_url="http://example.com/test.zip")
    assert "temp_dir" in result

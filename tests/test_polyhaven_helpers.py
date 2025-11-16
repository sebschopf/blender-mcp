import os
import sys

# Ensure the 'src' directory is importable for tests
TEST_ROOT = os.path.dirname(__file__)
SRC_PATH = os.path.abspath(os.path.join(TEST_ROOT, "..", "src"))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import blender_mcp.polyhaven as poly


class DummyResponse:
    def __init__(self, status_code: int, data: bytes | dict):
        self.status_code = status_code
        self._data = data

    def json(self):
        if isinstance(self._data, dict):
            return self._data
        raise ValueError("not json")

    @property
    def content(self):
        if isinstance(self._data, bytes):
            return self._data
        raise ValueError("not bytes")


def test_fetch_files_data_success(monkeypatch):
    called = {}

    def fake_get(url, headers=None, timeout=None):
        called["url"] = url
        return DummyResponse(200, {"color": {"1k": {"jpg": {"url": "https://example.com/c.jpg"}}}})

    class DummySession:
        def get(self, url, timeout=None, headers=None, params=None, **kwargs):
            return fake_get(url, headers=headers, timeout=timeout)

    monkeypatch.setattr("blender_mcp.http.get_session", lambda: DummySession())
    data = poly.fetch_files_data("asset123")
    assert "color" in data
    assert called["url"].endswith("/files/asset123")


def test_find_texture_map_urls():
    files_data = {
        "color": {"1k": {"jpg": {"url": "https://a/c.jpg"}}},
        "normal": {"1k": {"jpg": {"url": "https://a/n.jpg"}}},
        "gltf": {"1k": {"gltf": {"url": "https://a/model.gltf"}}},
    }
    res = poly.find_texture_map_urls(files_data, "1k", "jpg")
    assert res["color"].endswith("c.jpg")
    assert res["normal"].endswith("n.jpg")
    assert "gltf" not in res


def test_find_model_file_info():
    files_data = {"gltf": {"1k": {"gltf": {"url": "https://a/model.gltf", "include": {}}}}}
    fi = poly.find_model_file_info(files_data, "gltf", "1k")
    assert fi is not None
    assert fi.get("url").endswith("model.gltf")


def test_download_bytes(monkeypatch):
    def fake_get(url, timeout=None):
        return DummyResponse(200, b"abc")

    class DummySession:
        def get(self, url, timeout=None, headers=None, params=None, **kwargs):
            return fake_get(url, timeout=timeout)

    monkeypatch.setattr("blender_mcp.http.get_session", lambda: DummySession())
    b = poly.download_bytes("https://example.com/a.bin")
    assert b == b"abc"


def test_prepare_model_files(monkeypatch, tmp_path):
    # Prepare a fake file_info structure with includes
    file_info = {
        "url": "https://example.com/models/main.gltf",
        "include": {"textures/tex.png": {"url": "https://example.com/models/textures/tex.png"}},
    }

    def fake_download(url, timeout=None):
        # Return deterministic bytes depending on url
        return b"MAIN" if url.endswith("main.gltf") else b"INC"

    monkeypatch.setattr(poly, "download_bytes", fake_download)

    temp_dir, main_path = poly.prepare_model_files(file_info, base_temp_dir=str(tmp_path))
    assert main_path.startswith(str(tmp_path))
    assert "main.gltf" in main_path
    # Main file written
    with open(main_path, "rb") as fh:
        assert fh.read() == b"MAIN"

    # Included file written
    inc_path = tmp_path / "textures" / "tex.png"
    assert inc_path.exists()
    with open(inc_path, "rb") as fh:
        assert fh.read() == b"INC"


def test_fetch_categories(monkeypatch):
    called = {}

    def fake_get(url, headers=None, timeout=None):
        called["url"] = url
        return DummyResponse(200, {"hdris": 10, "textures": 20})

    class DummySession:
        def get(self, url, timeout=None, headers=None, params=None, **kwargs):
            return fake_get(url, headers=headers, timeout=timeout)

    monkeypatch.setattr("blender_mcp.http.get_session", lambda: DummySession())
    cats = poly.fetch_categories("hdris")
    assert isinstance(cats, dict)
    assert called["url"].endswith("/categories/hdris")


def test_search_assets(monkeypatch):
    called = {}

    def fake_get(url, params=None, headers=None, timeout=None):
        called["url"] = url
        called["params"] = params
        return DummyResponse(200, {"asset1": {"name": "A"}, "asset2": {"name": "B"}})

    class DummySession:
        def get(self, url, timeout=None, headers=None, params=None, **kwargs):
            return fake_get(url, params=params, headers=headers, timeout=timeout)

    monkeypatch.setattr("blender_mcp.http.get_session", lambda: DummySession())
    res = poly.search_assets({"type": "hdris", "categories": "sky"})
    assert "asset1" in res
    assert called["params"]["type"] == "hdris"

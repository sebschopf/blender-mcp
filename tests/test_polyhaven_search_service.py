import pytest

from blender_mcp.errors import ExternalServiceError, InvalidParamsError
from blender_mcp.services import polyhaven as svc_polyhaven


def test_polyhaven_search_success(monkeypatch):
    monkeypatch.setattr(
        svc_polyhaven,
        "search_assets_network",
        lambda **kwargs: {
            "assets": {"a1": {"name": "Asset One", "download_count": 10, "categories": ["wood"], "type": 2}},
            "total_count": 1,
            "returned_count": 1,
        },
    )
    res = svc_polyhaven.search_polyhaven_assets({"asset_type": "models", "categories": "wood"})
    assert res.get("status") == "success"
    result = res.get("result", {})
    assert result.get("total_count") == 1
    assert "a1" in result.get("assets", {})


def test_polyhaven_search_invalid_asset_type():
    with pytest.raises(InvalidParamsError):
        svc_polyhaven.search_polyhaven_assets({"asset_type": "notype"})


def test_polyhaven_search_invalid_categories_type():
    with pytest.raises(InvalidParamsError):
        svc_polyhaven.search_polyhaven_assets({"categories": ["wood"]})


def test_polyhaven_search_invalid_page():
    with pytest.raises(InvalidParamsError):
        svc_polyhaven.search_polyhaven_assets({"page": 0})


def test_polyhaven_search_invalid_per_page():
    with pytest.raises(InvalidParamsError):
        svc_polyhaven.search_polyhaven_assets({"per_page": 1000})


def test_polyhaven_search_network_error(monkeypatch):
    def boom(**kwargs):
        raise RuntimeError("network fail")

    monkeypatch.setattr(svc_polyhaven, "search_assets_network", boom)
    with pytest.raises(ExternalServiceError) as excinfo:
        svc_polyhaven.search_polyhaven_assets({"asset_type": "hdris"})
    assert "network fail" in str(excinfo.value)

import importlib

import pytest

from blender_mcp.errors import ExternalServiceError, InvalidParamsError
from blender_mcp.services import polyhaven as svc_polyhaven


def test_polyhaven_categories_success(monkeypatch):
    monkeypatch.setattr(
        svc_polyhaven,
        "fetch_categories",
        lambda api_base="https://api.polyhaven.com", asset_type="hdris", session=None: {"categories": {"a": 1}},
    )
    res = svc_polyhaven.get_polyhaven_categories({"asset_type": "textures"})
    assert res.get("status") == "success"
    assert res.get("result", {}).get("categories") == {"a": 1}


def test_polyhaven_categories_invalid_params():
    with pytest.raises(InvalidParamsError):
        svc_polyhaven.get_polyhaven_categories({"asset_type": 123})


def test_polyhaven_categories_network_error(monkeypatch):
    def boom(**kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(svc_polyhaven, "fetch_categories", boom)

    with pytest.raises(ExternalServiceError) as excinfo:
        svc_polyhaven.get_polyhaven_categories({"asset_type": "hdris"})
    assert "network down" in str(excinfo.value)

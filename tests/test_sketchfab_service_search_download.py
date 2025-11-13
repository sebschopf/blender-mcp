import os

import pytest

from blender_mcp.errors import ExternalServiceError, InvalidParamsError
from blender_mcp.services import sketchfab as svc_skfb


def test_search_requires_api_key(monkeypatch):
    if "SKETCHFAB_API_KEY" in os.environ:
        monkeypatch.delenv("SKETCHFAB_API_KEY", raising=False)
    with pytest.raises(InvalidParamsError):
        svc_skfb.search_sketchfab_models({"query": "chair"})


def test_search_uses_env_api_key(monkeypatch):
    monkeypatch.setenv("SKETCHFAB_API_KEY", "k")
    monkeypatch.setattr(
        svc_skfb._sketchfab,
        "search_models",
        lambda api_key, query, categories=None, count=20, downloadable=True: {"ok": True},
    )
    res = svc_skfb.search_sketchfab_models({"query": "chair", "count": 5})
    assert res["status"] == "success"
    assert res["result"]["ok"] is True


def test_search_maps_error(monkeypatch):
    monkeypatch.setenv("SKETCHFAB_API_KEY", "k")
    monkeypatch.setattr(
        svc_skfb._sketchfab, "search_models", lambda *a, **k: {"error": "bad"}
    )
    with pytest.raises(ExternalServiceError):
        svc_skfb.search_sketchfab_models({"query": "x"})


def test_download_success(monkeypatch):
    monkeypatch.setenv("SKETCHFAB_API_KEY", "k")
    monkeypatch.setattr(svc_skfb._sketchfab, "download_model", lambda api_key, uid: {"temp_dir": "T"})
    res = svc_skfb.download_sketchfab_model({"uid": "u1"})
    assert res["status"] == "success"
    assert res["result"]["temp_dir"] == "T"


def test_download_error(monkeypatch):
    monkeypatch.setenv("SKETCHFAB_API_KEY", "k")
    monkeypatch.setattr(svc_skfb._sketchfab, "download_model", lambda api_key, uid: {"error": "nope"})
    with pytest.raises(ExternalServiceError):
        svc_skfb.download_sketchfab_model({"uid": "u1"})

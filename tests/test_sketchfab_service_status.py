import pytest

from blender_mcp.services import sketchfab as svc_sketchfab


def test_sketchfab_status_no_key():
    res = svc_sketchfab.get_sketchfab_status_service({})
    assert res.get("status") == "success"
    body = res.get("result", {})
    assert body.get("enabled") is False
    assert "No API key" in body.get("message", "")


def test_sketchfab_status_with_key(monkeypatch):
    # mock underlying helper to avoid network
    monkeypatch.setattr(
        svc_sketchfab._sketchfab,
        "get_sketchfab_status",
        lambda api_key: {"enabled": True, "message": "Logged in as: test"},
    )
    res = svc_sketchfab.get_sketchfab_status_service({"api_key": "k"})
    assert res.get("status") == "success"
    body = res.get("result", {})
    assert body.get("enabled") is True
    assert "Logged in as" in body.get("message", "")


def test_sketchfab_status_invalid_param():
    from blender_mcp.errors import InvalidParamsError

    with pytest.raises(InvalidParamsError):
        svc_sketchfab.get_sketchfab_status_service({"api_key": 123})

from typing import Any, Dict

from blender_mcp.services import hyper3d_status as svc_h3d_status
from blender_mcp.services import polyhaven as svc_polyhaven
from blender_mcp.services import polyhaven_status as svc_ph_status


def test_polyhaven_status_success(monkeypatch):
    monkeypatch.setattr(svc_polyhaven, "fetch_categories", lambda **kwargs: {"categories": {"hdr": 1}})
    res: Dict[str, Any] = svc_ph_status.get_polyhaven_status_service()
    assert res["status"] == "success"
    assert res["result"]["enabled"] is True


def test_polyhaven_status_network_fail(monkeypatch):
    def boom(**kwargs):
        raise RuntimeError("no network")

    monkeypatch.setattr(svc_polyhaven, "fetch_categories", boom)
    res: Dict[str, Any] = svc_ph_status.get_polyhaven_status_service()
    assert res["status"] == "success"
    assert res["result"]["enabled"] is False


def test_hyper3d_status_success():
    res: Dict[str, Any] = svc_h3d_status.get_hyper3d_status_service()
    assert res["status"] == "success"
    assert res["result"]["enabled"] is True

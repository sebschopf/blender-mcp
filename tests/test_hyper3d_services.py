import pytest

from blender_mcp.errors import ExternalServiceError, InvalidParamsError
from blender_mcp.services import hyper3d as svc_h3d


def test_generate_text_fal_success(monkeypatch):
    monkeypatch.setattr(
        svc_h3d._h3d,
        "create_rodin_job_fal_ai",
        lambda api_key, text_prompt=None, images=None, bbox_condition=None: {"ok": True, "id": "rid"},
    )
    res = svc_h3d.generate_hyper3d_model_via_text(
        {"api_key": "k", "text_prompt": "chair", "bbox_condition": [1, 1, 1]}
    )
    assert res["status"] == "success"
    assert res["result"]["id"] == "rid"


def test_generate_images_fal_success(monkeypatch):
    monkeypatch.setattr(
        svc_h3d._h3d,
        "create_rodin_job_fal_ai",
        lambda api_key, text_prompt=None, images=None, bbox_condition=None: {"ok": True, "id": "rid2"},
    )
    res = svc_h3d.generate_hyper3d_model_via_images(
        {"api_key": "k", "input_image_urls": ["http://u"], "bbox_condition": [1, 1, 1]}
    )
    assert res["status"] == "success"
    assert res["result"]["id"] == "rid2"


def test_generate_images_invalid_urls():
    with pytest.raises(InvalidParamsError):
        svc_h3d.generate_hyper3d_model_via_images({"api_key": "k", "input_image_urls": []})


def test_poll_fal_success(monkeypatch):
    monkeypatch.setattr(
        svc_h3d._h3d, "poll_rodin_job_status_fal_ai", lambda api_key, request_id: {"state": "done"}
    )
    res = svc_h3d.poll_rodin_job_status({"api_key": "k", "request_id": "r1"})
    assert res["status"] == "success"
    assert res["result"]["state"] == "done"


def test_poll_main_site_success(monkeypatch):
    monkeypatch.setattr(
        svc_h3d._h3d, "poll_rodin_job_status_main_site", lambda api_key, subscription_key: {"status_list": ["ok"]}
    )
    res = svc_h3d.poll_rodin_job_status({"api_key": "k", "subscription_key": "s1"})
    assert res["result"]["status_list"] == ["ok"]


def test_import_fal_success(monkeypatch):
    monkeypatch.setattr(
        svc_h3d._h3d,
        "import_generated_asset_fal_ai",
        lambda api_key, request_id, name: {"succeed": True, "temp_file": "p"},
    )
    res = svc_h3d.import_generated_asset({"api_key": "k", "request_id": "r1", "name": "obj"})
    assert res["status"] == "success"
    assert res["result"]["succeed"] is True


def test_import_main_site_success(monkeypatch):
    monkeypatch.setattr(
        svc_h3d._h3d,
        "import_generated_asset_main_site",
        lambda api_key, task_uuid, name: {"succeed": True, "temp_file": "p"},
    )
    res = svc_h3d.import_generated_asset({"api_key": "k", "task_uuid": "t1", "name": "obj"})
    assert res["result"]["succeed"] is True


def test_generate_text_network_error(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("network")

    monkeypatch.setattr(svc_h3d._h3d, "create_rodin_job_fal_ai", boom)
    with pytest.raises(ExternalServiceError):
        svc_h3d.generate_hyper3d_model_via_text({"api_key": "k", "text_prompt": "chair"})

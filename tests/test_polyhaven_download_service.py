import pytest

from blender_mcp.errors import ExternalServiceError, InvalidParamsError
from blender_mcp.services import polyhaven as svc_polyhaven


def test_polyhaven_download_success(monkeypatch, tmp_path):
    fake_dir = tmp_path / "extracted"
    fake_dir.mkdir()

    monkeypatch.setattr(
        svc_polyhaven,
        "download_asset",
        lambda **kwargs: {"temp_dir": str(fake_dir)},
    )
    res = svc_polyhaven.download_polyhaven_asset(
        {"asset_id": "a1", "asset_type": "models", "resolution": "1k"}
    )
    assert res.get("status") == "success"
    assert res.get("result", {}).get("temp_dir").endswith("extracted")


ess_cases = [
    ({}, "asset_id"),
    ({"asset_id": 123, "asset_type": "hdris"}, "asset_id"),
    ({"asset_id": "a1"}, "asset_type"),
    ({"asset_id": "a1", "asset_type": "foo"}, "asset_type"),
    ({"asset_id": "a1", "asset_type": "hdris", "resolution": 10}, "resolution"),
    ({"asset_id": "a1", "asset_type": "hdris", "file_format": 10}, "file_format"),
]


@pytest.mark.parametrize("params,bad", ess_cases)
def test_polyhaven_download_invalid_params(params, bad):
    with pytest.raises(InvalidParamsError):
        svc_polyhaven.download_polyhaven_asset(params)


def test_polyhaven_download_network_error(monkeypatch):
    def boom(**kwargs):
        raise RuntimeError("download failed")

    monkeypatch.setattr(svc_polyhaven, "download_asset", boom)

    with pytest.raises(ExternalServiceError) as excinfo:
        svc_polyhaven.download_polyhaven_asset(
            {"asset_id": "a2", "asset_type": "textures", "resolution": "2k"}
        )
    assert "download failed" in str(excinfo.value)

from typing import Any, Dict

import pytest

from blender_mcp.errors import ExternalServiceError, HandlerError, InvalidParamsError
from blender_mcp.services import object as svc_object


def test_missing_name_raises_invalid_params() -> None:
    with pytest.raises(InvalidParamsError):
        svc_object.get_object_info(None)


def test_addon_returns_error_dict_monkeypatched(monkeypatch: pytest.MonkeyPatch) -> None:
    # addon reports bpy missing
    def _fake(name: str) -> Dict[str, Any]:
        return {"error": "Blender (bpy) not available"}

    monkeypatch.setattr(svc_object, "_addon_get_object_info", _fake)
    with pytest.raises(ExternalServiceError):
        svc_object.get_object_info({"name": "Cube"})


def test_addon_raises_wrapped_as_handler_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(name: str) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(svc_object, "_addon_get_object_info", _raise)

    with pytest.raises(HandlerError) as exc:
        svc_object.get_object_info({"name": "Cube"})
    assert "get_object_info" in str(exc.value)


def test_addon_success_returns_success_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    sample: Dict[str, Any] = {"name": "Cube", "type": "MESH", "location": [1.0, 2.0, 3.0]}

    def _return(name: str) -> Dict[str, Any]:
        return sample

    monkeypatch.setattr(svc_object, "_addon_get_object_info", _return)

    res = svc_object.get_object_info({"name": "Cube"})
    assert res["status"] == "success"
    assert res["object"]["name"] == "Cube"

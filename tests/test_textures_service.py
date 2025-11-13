import pytest

from blender_mcp.errors import HandlerError, InvalidParamsError
from blender_mcp.services import textures as svc_textures


def test_set_texture_success_material(monkeypatch):
    monkeypatch.setattr(
        svc_textures, "_addon_set_texture", lambda obj, tex: {"success": True, "material": "matA"}
    )
    res = svc_textures.set_texture({"object_name": "Cube", "texture_id": "wood_01"})
    assert res["status"] == "success"
    assert res["result"]["material"] == "matA"


def test_set_texture_success_images(monkeypatch):
    monkeypatch.setattr(
        svc_textures, "_addon_set_texture", lambda obj, tex: {"images": ["color", "normal"]}
    )
    res = svc_textures.set_texture({"object_name": "Cube", "texture_id": "wood_01"})
    assert res["status"] == "success"
    assert set(res["result"]["images"]) == {"color", "normal"}


def test_set_texture_invalid_params():
    with pytest.raises(InvalidParamsError):
        svc_textures.set_texture({})
    with pytest.raises(InvalidParamsError):
        svc_textures.set_texture({"object_name": 1, "texture_id": "x"})
    with pytest.raises(InvalidParamsError):
        svc_textures.set_texture({"object_name": "Cube", "texture_id": 2})


def test_set_texture_addon_error(monkeypatch):
    monkeypatch.setattr(
        svc_textures, "_addon_set_texture", lambda obj, tex: {"error": "boom"}
    )
    with pytest.raises(HandlerError):
        svc_textures.set_texture({"object_name": "Cube", "texture_id": "wood_01"})


def test_set_texture_addon_exception(monkeypatch):
    def boom(obj, tex):
        raise RuntimeError("crash")

    monkeypatch.setattr(svc_textures, "_addon_set_texture", boom)
    with pytest.raises(HandlerError):
        svc_textures.set_texture({"object_name": "Cube", "texture_id": "wood_01"})

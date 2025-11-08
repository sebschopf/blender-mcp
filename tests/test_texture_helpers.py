"""Tests for texture_helpers using fake image objects and fake loader."""
from __future__ import annotations

from dataclasses import dataclass

from blender_mcp import texture_helpers


@dataclass
class FakeColorspace:
    name: str = ""


class FakeImage:
    def __init__(self) -> None:
        self.name = ""
        self.colorspace_settings = FakeColorspace()
        self.packed_file = None
        self._packed_called = False

    def pack(self) -> None:
        self._packed_called = True
        self.packed_file = object()


def test_configure_image_sets_colorspace_and_packs():
    img = FakeImage()
    # color map
    texture_helpers.configure_image(img, "color", pack_if_missing=True)
    assert img.colorspace_settings.name == "sRGB"
    assert img._packed_called is True

    # reset
    img = FakeImage()
    # non-color map
    texture_helpers.configure_image(img, "roughness", pack_if_missing=True)
    assert img.colorspace_settings.name == "Non-Color"
    assert img._packed_called is True


def test_load_and_configure_image_uses_loader_and_sets_name():
    img = FakeImage()

    def loader(path: str):
        assert path == "some/path.png"
        return img

    res = texture_helpers.load_and_configure_image(
        "some/path.png", "albedo", name="texname", loader=loader
    )
    assert res is img
    assert img.name == "texname"
    assert img.colorspace_settings.name == "sRGB"

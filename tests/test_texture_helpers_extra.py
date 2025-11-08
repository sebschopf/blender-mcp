from __future__ import annotations

import types

from blender_mcp import texture_helpers


class FakeImage:
    def __init__(self):
        self.name = ""
        self.packed_file = None

        class CS:
            def __init__(self):
                self.name = ""

        self.colorspace_settings = CS()

    def pack(self):
        self.packed_file = True


def test_load_and_configure_image_color_map(monkeypatch, tmp_path):
    # Create a fake loader
    def fake_loader(path: str):
        return FakeImage()

    img = texture_helpers.load_and_configure_image(
        path=str(tmp_path / "img.jpg"), map_type="color", name="tex_name", loader=fake_loader
    )

    assert img.name == "tex_name"
    assert img.colorspace_settings.name == "sRGB"
    assert img.packed_file is True


def test_load_and_configure_image_non_color_map(monkeypatch, tmp_path):
    def fake_loader(path: str):
        img = types.SimpleNamespace()
        # No colorspace_settings attribute to simulate minimal object
        img.packed_file = None

        def pack():
            img.packed_file = True

        img.pack = pack
        return img

    img = texture_helpers.load_and_configure_image(
        path=str(tmp_path / "n.png"), map_type="normal", name="nmap", loader=fake_loader
    )

    # Name should be set even on SimpleNamespace
    assert getattr(img, "name", None) == "nmap"
    # Non-color mapping should set Non-Color when possible: our fake lacks colorspace_settings,
    # but function should not raise and pack should be called
    assert img.packed_file is True

import base64
import sys
import types

from blender_mcp.services.screenshot import get_viewport_screenshot


def test_get_viewport_screenshot_with_bpy(monkeypatch):
    # Create fake bpy with capture_viewport_bytes helper
    def fake_capture():
        return b"\x89PNG\r\n...PNGDATA"

    fake_bpy = types.SimpleNamespace()
    fake_bpy.capture_viewport_bytes = fake_capture
    sys.modules["bpy"] = fake_bpy

    try:
        resp = get_viewport_screenshot()
        assert resp["status"] == "success"
        decoded = base64.b64decode(resp["image_base64"].encode("ascii"))
        assert decoded.startswith(b"\x89PNG")
    finally:
        del sys.modules["bpy"]


def test_get_viewport_screenshot_no_bpy():
    if "bpy" in sys.modules:
        del sys.modules["bpy"]
    resp = get_viewport_screenshot()
    assert resp["status"] == "error"

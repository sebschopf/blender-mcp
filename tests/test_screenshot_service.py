import importlib
import sys
import types

from blender_mcp.services import screenshot


def test_screenshot_no_bpy(monkeypatch):
    monkeypatch.delitem(sys.modules, "bpy", raising=False)
    importlib.reload(screenshot)
    res = screenshot.get_viewport_screenshot()
    assert res.get("status") == "error"
    assert "Blender (bpy) not available" in res.get("message", "")


def test_screenshot_no_helper(monkeypatch):
    fake = types.ModuleType("bpy")
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(screenshot)
    res = screenshot.get_viewport_screenshot()
    assert res.get("status") == "error"
    assert "capture_viewport_bytes not available" in res.get("message", "")


def test_screenshot_helper_returns_non_bytes(monkeypatch):
    fake = types.ModuleType("bpy")
    fake.capture_viewport_bytes = lambda: "not-bytes"
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(screenshot)
    res = screenshot.get_viewport_screenshot()
    assert res.get("status") == "error"
    assert "capture returned non-bytes" in res.get("message", "")


def test_screenshot_success(monkeypatch):
    fake = types.ModuleType("bpy")
    fake.capture_viewport_bytes = lambda: b"\x89PNG\r\n"
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(screenshot)
    res = screenshot.get_viewport_screenshot()
    assert res.get("status") == "success"
    assert "image_base64" in res


def test_screenshot_helper_raises(monkeypatch):
    fake = types.ModuleType("bpy")

    def bad():
        raise RuntimeError("boom")

    fake.capture_viewport_bytes = bad
    monkeypatch.setitem(sys.modules, "bpy", fake)
    importlib.reload(screenshot)
    res = screenshot.get_viewport_screenshot()
    assert res.get("status") == "error"
    assert "boom" in res.get("message", "")

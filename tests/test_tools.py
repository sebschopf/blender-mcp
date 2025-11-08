
from unittest.mock import Mock, patch

from blender_mcp import tools


def test_get_scene_info_returns_json_string():
    fake = Mock()
    fake.send_command.return_value = {"scene": "ok"}

    with patch("blender_mcp.tools.get_blender_connection", return_value=fake):
        res = tools.get_scene_info(None)
        assert isinstance(res, str)
        assert '"scene": "ok"' in res


def test_execute_blender_code_success():
    fake = Mock()
    fake.send_command.return_value = {"result": "done"}

    with patch("blender_mcp.tools.get_blender_connection", return_value=fake):
        res = tools.execute_blender_code(None, "print(1)")
        assert "Code executed successfully" in res


def test_get_viewport_screenshot_reads_tempfile(tmp_path, monkeypatch):
    # the stubbed blender will write to a temp path provided by the code under test

    def fake_send_command(cmd_type, params=None):
        # write a small PNG-like header to the expected filepath
        fp = params.get("filepath")
        with open(fp, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")
        return {}

    fake = Mock()
    fake.send_command.side_effect = fake_send_command

    with patch("blender_mcp.tools.get_blender_connection", return_value=fake):
        img = tools.get_viewport_screenshot(None, max_size=10)
        # Image returned by mcp has attributes .data (bytes) and .format
        assert hasattr(img, "data")
        assert isinstance(img.data, (bytes, bytearray))
        assert getattr(img, "format", "png") == "png"

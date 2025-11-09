import json

import importlib.util
from pathlib import Path

# Load the repository-root `blender_mcp/server.py` archive shim so tests exercise
# the legacy BlenderConnection implementation. We can't import it as
# `blender_mcp.server` because the test PYTHONPATH points at `src/`.
root_server_path = Path(__file__).resolve().parents[1] / "blender_mcp" / "server.py"
spec = importlib.util.spec_from_file_location("blender_mcp_root_server", str(root_server_path))
srv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srv)  # type: ignore


class FakeSocket:
    def __init__(self, responses=None):
        self._responses = responses or []
        self.sent = b""
        self.timeout = None

    def settimeout(self, t):
        self.timeout = t

    def connect(self, addr):
        # succeed silently
        return None

    def close(self):
        return None

    def sendall(self, data: bytes):
        self.sent += data

    def recv(self, bufsize=8192):
        if not self._responses:
            return b""
        return self._responses.pop(0)


def test_blender_connection_connect_success(monkeypatch):
    fake = FakeSocket()

    class SockFactory:
        def __call__(self, *a, **k):
            return fake

    monkeypatch.setattr(srv.socket, "socket", SockFactory())

    conn = srv.BlenderConnection(host="h", port=1234, timeout=0.1)
    ok = conn.connect()
    assert ok is True
    assert conn.sock is fake
    conn.disconnect()
    assert conn.sock is None


def test_blender_connection_send_command_roundtrip(monkeypatch):
    # Prepare a fake socket that returns a JSON response in one chunk
    resp = json.dumps({"status": "ok", "result": {"x": 1}}).encode("utf-8")
    fake = FakeSocket(responses=[resp])

    class SockFactory:
        def __call__(self, *a, **k):
            return fake

    monkeypatch.setattr(srv.socket, "socket", SockFactory())

    conn = srv.BlenderConnection()
    assert conn.connect() is True
    res = conn.send_command("get_scene_info", params={})
    assert res["status"] == "ok"
    conn.disconnect()

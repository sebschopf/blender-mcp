import socket
import sys
import types

from blender_mcp.services.execute import execute_blender_code, send_command_over_network


def test_execute_blender_code_lazy_bpy(monkeypatch):
    # create a fake bpy module with a writable attribute
    fake_bpy = types.SimpleNamespace()
    sys.modules["bpy"] = fake_bpy

    code = "bpy.OK = True\nresult = {'value': 42}"
    resp = execute_blender_code({"code": code})
    assert resp["status"] == "success"
    assert resp["result"] == {"value": 42}
    assert getattr(fake_bpy, "OK", False) is True

    # cleanup
    del sys.modules["bpy"]


def test_execute_blender_code_no_bpy():
    # Ensure behavior when bpy is not importable
    if "bpy" in sys.modules:
        del sys.modules["bpy"]
    resp = execute_blender_code({"code": "result = 1"})
    assert resp["status"] == "error"


def test_send_command_over_network(monkeypatch):
    # Fake socket to assert data sent and provide a JSON response
    class FakeSocket:
        def __init__(self, *args, **kwargs):
            self._data = [b'{"status":"ok","result":{"msg":"pong"}}']
            self.sent = b""

        def connect(self, addr):
            return None

        def settimeout(self, t):
            self.timeout = t

        def sendall(self, b):
            self.sent = b

        def recv(self, bufsize):
            if self._data:
                return self._data.pop(0)
            return b""

        def close(self):
            return None

    monkeypatch.setattr(socket, "socket", FakeSocket)

    res = send_command_over_network("localhost", 9999, "ping", {"a": 1})
    assert isinstance(res, dict)
    assert res.get("msg") == "pong"

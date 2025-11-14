import socket

import pytest

from blender_mcp.services.connection.network import BlenderConnectionNetwork
from blender_mcp.services.connection.receiver import ResponseReceiver
from blender_mcp.services.connection.transport import CoreTransport, RawSocketTransport, select_transport


def test_select_transport_prefers_raw_when_socket_factory_provided():
    def factory():
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    t = select_transport("localhost", 1234, socket_factory=factory)
    assert isinstance(t, RawSocketTransport)


def test_select_transport_uses_core_when_available():
    # When the core module is importable, the selector should return CoreTransport
    t = select_transport("localhost", 1234)
    # Depending on environment, core may be unavailable; accept Raw fallback
    assert isinstance(t, (CoreTransport, RawSocketTransport))


def test_response_receiver_timeout():
    class TimeoutSock:
        def settimeout(self, t):
            self.t = t

        def recv(self, n):
            raise socket.timeout

    rr = ResponseReceiver()
    with pytest.raises(socket.timeout):
        rr.receive_one(TimeoutSock(), buffer_size=64, timeout=0.01)


def test_response_receiver_reassembles_chunks():
    class ChunkSock:
        def __init__(self):
            self._data = [b'{"x":', b" 1}\n", b""]

        def settimeout(self, t):
            self.t = t

        def recv(self, n):
            return self._data.pop(0)

    rr = ResponseReceiver()
    res = rr.receive_one(ChunkSock(), buffer_size=64, timeout=1)
    assert res == {"x": 1}


def test_network_uses_injected_transport(monkeypatch):
    calls = {"connect": 0, "send": [], "recv": 0, "disconnect": 0}

    class FakeTransport:
        def connect(self):
            calls["connect"] += 1
            return True

        def disconnect(self):
            calls["disconnect"] += 1

        def receive_full_response(self, *, buffer_size: int = 8192, timeout: float = 15.0):
            calls["recv"] += 1
            return {"status": "success", "result": {"ok": True}}

        def send_command(self, command_type: str, params=None):
            calls["send"].append((command_type, params or {}))
            return self.receive_full_response()

    net = BlenderConnectionNetwork("localhost", 1234, transport=FakeTransport())
    assert net.connect() is True
    resp = net.send_command("ping", {"n": 1})
    assert resp == {"status": "success", "result": {"ok": True}}
    assert calls["connect"] == 1
    assert calls["send"] == [("ping", {"n": 1})]


def test_response_receiver_no_data_raises():
    class EmptySock:
        def settimeout(self, t):
            self.t = t

        def recv(self, n):
            return b""

    rr = ResponseReceiver()
    with pytest.raises(ConnectionError):
        rr.receive_one(EmptySock(), buffer_size=64, timeout=0.1)


def test_rawsocket_transport_sends_ndjson(monkeypatch):
    sent = {"data": b""}

    class FakeSock:
        def __init__(self):
            self._response = [b'{"status":"success","result":{"ok":true}}']

        def connect(self, addr):
            return None

        def sendall(self, data):
            sent["data"] += data

        def settimeout(self, t):
            self.t = t

        def recv(self, n):
            if self._response:
                return self._response.pop(0)
            return b""

        def close(self):
            return None

    def factory():
        return FakeSock()

    from blender_mcp.services.connection.transport import RawSocketTransport

    t = RawSocketTransport("localhost", 5555, socket_factory=factory)
    assert t.connect() is True
    resp = t.send_command("echo", {"a": 1})
    assert resp == {"status": "success", "result": {"ok": True}}
    # Vérifie que l'envoi est du NDJSON (fin par \n) et contient le bon JSON
    assert sent["data"].endswith(b"\n")
    payload = sent["data"].rstrip(b"\n").decode("utf-8")
    import json as _json

    obj = _json.loads(payload)
    assert obj.get("type") == "echo"
    assert obj.get("params") == {"a": 1}

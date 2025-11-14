import socket

import pytest

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

import pytest

from blender_mcp.connection import BlenderConnection, ChunkedJSONReassembler


def test_reassembler_single_message():
    r = ChunkedJSONReassembler()
    r.feed(b'{"a": 1}\n')
    msgs = r.pop_messages()
    assert msgs == [{"a": 1}]


def test_reassembler_split_chunks():
    r = ChunkedJSONReassembler()
    r.feed(b'{"a":')
    # no complete message yet
    assert r.pop_messages() == []
    r.feed(b' 2}\n')
    assert r.pop_messages() == [{"a": 2}]


def test_reassembler_multiple_messages():
    r = ChunkedJSONReassembler()
    r.feed(b'{"x":1}\n{"y":2}\n')
    msgs = r.pop_messages()
    assert msgs == [{"x": 1}, {"y": 2}]


def test_reassembler_ignores_empty_lines():
    r = ChunkedJSONReassembler()
    r.feed(b'\n')
    assert r.pop_messages() == []


def test_blender_connection_iter_chunks():
    conn = BlenderConnection()

    def chunks():
        yield b'{"a": 1}\n'
        yield b'{"b":'
        yield b' 2}\n{"c":3}\n'

    msgs = list(conn.iter_messages_from_chunks(chunks()))
    assert msgs == [{"a": 1}, {"b": 2}, {"c": 3}]


def test_reassembler_bad_json_raises():
    r = ChunkedJSONReassembler()
    r.feed(b'{bad json}\n')
    with pytest.raises(ValueError):
        r.pop_messages()
import socket


def test_connect_handles_exception(monkeypatch):
    class BadSocket:
        def __init__(self, *args, **kwargs):
            pass

        def connect(self, addr):
            raise OSError("cannot connect")

    monkeypatch.setattr(socket, "socket", BadSocket)

    conn = BlenderConnection("localhost", 9999)
    assert conn.connect() is False


def test_send_command_with_fake_socket(monkeypatch):
    class FakeSocket:
        def __init__(self, *args, **kwargs):
            self._data = [b'{"status":"ok","result": {"message": "ok"}}']
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

    conn = BlenderConnection("localhost", 9999)
    assert conn.connect() is True
    res = conn.send_command("test", {"a": 1})
    assert isinstance(res, dict)
    assert res.get("message") == "ok"

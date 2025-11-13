import json
import socket
from typing import List

import pytest

from blender_mcp.connection import BlenderConnection


class FakeSocket:
    def __init__(self, recv_chunks: List[bytes], fail_connect: bool = False, timeout_after: int | None = None):
        self._chunks = list(recv_chunks)
        self._timeout_after = timeout_after
        self._recv_calls = 0
        self._closed = False
        self._fail_connect = fail_connect
        self.sent: bytes = b""
        self._timeout = 1.0

    def settimeout(self, value: float) -> None:  # pragma: no cover - trivial
        self._timeout = value

    def connect(self, address):  # pragma: no cover - trivial
        if self._fail_connect:
            raise OSError("connect failed")

    def recv(self, bufsize: int) -> bytes:
        if self._timeout_after is not None and self._recv_calls >= self._timeout_after:
            raise socket.timeout()
        self._recv_calls += 1
        return self._chunks.pop(0) if self._chunks else b""

    def sendall(self, data: bytes) -> None:
        self.sent += data

    def close(self) -> None:  # pragma: no cover - trivial
        self._closed = True


def test_send_command_reassembles_fragments():
    payload = {"status": "success", "result": 42}
    raw = json.dumps(payload).encode("utf-8")
    # Fragment the JSON arbitrarily
    chunks = [raw[:10], raw[10:20], raw[20:]]

    def factory():
        return FakeSocket(chunks)

    conn = BlenderConnection(socket_factory=factory)
    assert conn.connect() is True
    result = conn.send_command("echo", {"value": 42})
    # Network facade returns the 'result' field directly on success
    assert result == 42


def test_send_command_timeout_partial_json():
    payload = {"status": "success", "result": 1}
    raw = json.dumps(payload).encode("utf-8")
    # Provide only first part then trigger timeout
    partial = [raw[:8]]

    def factory():
        return FakeSocket(partial, timeout_after=1)

    conn = BlenderConnection(socket_factory=factory)
    assert conn.connect() is True
    with pytest.raises(Exception):
        conn.send_command("partial", {})


def test_connect_failure():
    def factory():
        return FakeSocket([], fail_connect=True)

    conn = BlenderConnection(socket_factory=factory)
    assert conn.connect() is False
    with pytest.raises(ConnectionError):
        conn.send_command("any", {})

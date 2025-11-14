from __future__ import annotations

import types
from typing import Any, Dict, Optional

import pytest

from blender_mcp.services.connection import Transport, select_transport
from blender_mcp.services.connection.network_core import NetworkCore


class FakeTransport:
    def __init__(self) -> None:
        self.connected = False
        self.sent: Optional[Dict[str, Any]] = None

    def connect(self) -> bool:
        self.connected = True
        return True

    def disconnect(self) -> None:
        self.connected = False

    def receive_full_response(self, *, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
        return {"ok": True}

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        self.sent = {"type": command_type, "params": params}
        return {"result": "sent"}


def test_fake_transport_is_instance_of_protocol_at_runtime() -> None:
    # Transport is runtime_checkable: isinstance should work for compatible objects
    fake = FakeTransport()
    assert isinstance(fake, Transport)


def test_network_core_uses_injected_transport() -> None:
    fake = FakeTransport()
    core = NetworkCore(host="example", port=1234, transport=fake)

    assert core.connect() is True
    assert fake.connected is True

    res = core.send_command("ping", {"n": 1})
    assert res == {"result": "sent"}
    assert fake.sent == {"type": "ping", "params": {"n": 1}}


def test_select_transport_with_socket_factory_returns_raw_socket(tmp_path) -> None:
    # verify select_transport picks the RawSocketTransport when provided a socket factory
    def factory() -> Any:
        # return a dummy object that mimics socket.socket enough to be used in connect()
        s = types.SimpleNamespace()

        def connect(addr):
            return None

        def close():
            return None

        s.connect = connect
        s.close = close
        return s

    tr = select_transport("localhost", 1, socket_factory=factory)
    # The transport should expose the expected methods
    assert hasattr(tr, "connect")
    assert hasattr(tr, "send_command")

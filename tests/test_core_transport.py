from __future__ import annotations

import importlib
from typing import Any, Dict, Optional

import pytest


class DummyCoreConn:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.connected = False
        self._buffer = b''

    def connect(self) -> bool:
        self.connected = True
        return True

    def disconnect(self) -> None:
        self.connected = False

    def _receive_full_response(self, buffer_size: int = 8192) -> bytes:
        return b'{"ok": true}'

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"result": {"type": command_type, "params": params or {}}}


def test_core_transport_uses_connection_core(monkeypatch) -> None:
    # Replace the real BlenderConnection with our dummy
    mod = importlib.import_module("blender_mcp.connection_core")
    monkeypatch.setattr(mod, "BlenderConnection", DummyCoreConn)

    # Import CoreTransport from services module (reload to pick monkeypatched symbol)
    transport_mod = importlib.import_module("blender_mcp.services.connection.transport")
    importlib.reload(transport_mod)

    CoreTransport = transport_mod.CoreTransport

    tr = CoreTransport("host", 1234)
    assert tr.connect() is True
    res = tr.send_command("hello", {"x": 1})
    assert isinstance(res, dict)
    # Expect the dummy to have returned wrapped result
    assert res.get("result", {}).get("type") == "hello"
    tr.disconnect()


def test_core_transport_send_raises(monkeypatch) -> None:
    class BrokenConn:
        def __init__(self, host: str, port: int) -> None:
            pass

        def connect(self) -> bool:
            return True

        def disconnect(self) -> None:
            return None

        def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            raise RuntimeError("core send failed")

    mod = importlib.import_module("blender_mcp.connection_core")
    monkeypatch.setattr(mod, "BlenderConnection", BrokenConn)
    transport_mod = importlib.import_module("blender_mcp.services.connection.transport")
    importlib.reload(transport_mod)
    CoreTransport = transport_mod.CoreTransport

    tr = CoreTransport("host", 1234)
    assert tr.connect() is True
    with pytest.raises(RuntimeError):
        tr.send_command("x", {})
    tr.disconnect()


def test_core_transport_receive_raises(monkeypatch) -> None:
    class BrokenConn2:
        def __init__(self, host: str, port: int) -> None:
            pass

        def connect(self) -> bool:
            return True

        def disconnect(self) -> None:
            return None

        def _receive_full_response(self, buffer_size: int = 8192) -> bytes:
            raise RuntimeError("receive failed")

        def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            return {"result": {}}

    mod = importlib.import_module("blender_mcp.connection_core")
    monkeypatch.setattr(mod, "BlenderConnection", BrokenConn2)
    transport_mod = importlib.import_module("blender_mcp.services.connection.transport")
    importlib.reload(transport_mod)
    CoreTransport = transport_mod.CoreTransport

    tr = CoreTransport("host", 1234)
    assert tr.connect() is True
    with pytest.raises(RuntimeError):
        tr.receive_full_response()
    tr.disconnect()

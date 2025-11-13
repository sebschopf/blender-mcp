"""Testable BlenderConnection implementation.

Provides a small, injectable API for socket communication with the
Blender addon. The goal is to support unit tests without requiring
real network connections.

Public API:
 - BlenderConnection(host, port, timeout, socket_factory)
 - connect()/disconnect()
 - send_command(type, params) -> dict
 - receive_full_response() -> bytes (public for advanced tests)
 - get_blender_connection() singleton accessor
 - server_lifespan() async context manager for ASGI adapters

Testing hooks:
 - `socket_factory` can be injected to return a fake socket with
   `connect`, `settimeout`, `recv`, `sendall`, `close` methods.

Fragment reassembly strategy:
 - Accumulate bytes until a valid top-level JSON document loads.
 - Stop on empty recv or timeout; attempt final parse, else raise.
"""
from __future__ import annotations

import json
import logging
import os
import socket
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Callable, Dict, Optional, Protocol

logger = logging.getLogger(__name__)

DEFAULT_HOST = os.getenv("BLENDER_HOST", "localhost")
DEFAULT_PORT = int(os.getenv("BLENDER_PORT", 9876))


class SocketLike(Protocol):  # minimal protocol for injection
    def settimeout(self, value: float) -> None: ...
    def connect(self, address: tuple[str, int]) -> None: ...
    def recv(self, bufsize: int) -> bytes: ...
    def sendall(self, data: bytes) -> None: ...
    def close(self) -> None: ...


def _default_socket_factory() -> SocketLike:
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class BlenderConnection:
    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        timeout: float = 15.0,
        *,
        socket_factory: Callable[[], SocketLike] = _default_socket_factory,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket_factory = socket_factory
        self.sock: Optional[SocketLike] = None

    # Life-cycle -------------------------------------------------
    def connect(self) -> bool:
        if self.sock:
            return True
        try:
            s = self._socket_factory()
            s.settimeout(self.timeout)
            s.connect((self.host, self.port))
            self.sock = s
            logger.debug("BlenderConnection connected %s:%s", self.host, self.port)
            return True
        except Exception:
            logger.exception("BlenderConnection failed to connect %s:%s", self.host, self.port)
            self.sock = None
            return False

    def disconnect(self) -> None:
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                logger.exception("Error closing BlenderConnection socket")
            finally:
                self.sock = None

    # Data flow --------------------------------------------------
    def receive_full_response(self, buffer_size: int = 8192) -> bytes:
        if not self.sock:
            raise ConnectionError("Not connected")
        chunks: list[bytes] = []
        self.sock.settimeout(self.timeout)
        while True:
            try:
                chunk = self.sock.recv(buffer_size)
            except socket.timeout:  # type: ignore[attr-defined]
                break
            if not chunk:
                break
            chunks.append(chunk)
            data = b"".join(chunks)
            try:
                json.loads(data.decode("utf-8"))
                return data
            except json.JSONDecodeError:
                continue
        data = b"".join(chunks)
        try:
            json.loads(data.decode("utf-8"))
            return data
        except Exception:
            logger.error("Incomplete JSON response from BlenderConnection")
            raise

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Blender")
        payload: Dict[str, Any] = {"type": command_type, "params": params or {}}
        assert self.sock is not None
        try:
            self.sock.sendall(json.dumps(payload).encode("utf-8"))
            raw = self.receive_full_response()
            return json.loads(raw.decode("utf-8"))
        except Exception:
            logger.exception("Error during send_command; dropping socket")
            self.sock = None
            raise


_singleton: Optional[BlenderConnection] = None


def get_blender_connection() -> BlenderConnection:
    global _singleton
    if _singleton is not None:
        return _singleton
    conn = BlenderConnection()
    if not conn.connect():
        raise ConnectionError("Could not connect to Blender. Ensure the addon is running.")
    _singleton = conn
    return conn


@asynccontextmanager
async def server_lifespan(server: "Any") -> AsyncIterator[Dict[str, Any]]:
    try:
        try:
            get_blender_connection()
        except Exception:
            logger.debug("Blender unreachable at startup; continuing")
        yield {}
    finally:
        global _singleton
        if _singleton:
            try:
                _singleton.disconnect()
            except Exception:
                logger.exception("Error disconnecting BlenderConnection during shutdown")
            _singleton = None


__all__ = [
    "BlenderConnection",
    "get_blender_connection",
    "server_lifespan",
    "SocketLike",
]

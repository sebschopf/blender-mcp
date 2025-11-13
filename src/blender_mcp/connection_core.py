"""Core BlenderConnection implementation (unique module name to avoid
collisions with the refactored services.connection package).

This mirrors the consolidated connection logic and is intended to be
imported explicitly by the repository-root shim to provide a single
authoritative implementation.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import warnings as _warnings
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Optional

logger = logging.getLogger(__name__)

_warnings.warn(
    (
        "blender_mcp.connection_core is deprecated; migrate to "
        "blender_mcp.services.connection.network_core and blender_mcp.connection."
    ),
    DeprecationWarning,
    stacklevel=2,
)

DEFAULT_HOST = os.getenv("BLENDER_HOST", "localhost")
DEFAULT_PORT = int(os.getenv("BLENDER_PORT", 9876))


class BlenderConnection:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 15.0) -> None:
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self.timeout = timeout

    def connect(self) -> bool:
        if self.sock:
            return True
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            s.connect((self.host, self.port))
            self.sock = s
            logger.info("Connected to Blender at %s:%s", self.host, self.port)
            return True
        except Exception:
            logger.exception("Failed to connect to Blender at %s:%s", self.host, self.port)
            self.sock = None
            return False

    def disconnect(self) -> None:
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                logger.exception("Error closing Blender socket")
            finally:
                self.sock = None

    def _receive_full_response(self, buffer_size: int = 8192) -> bytes:
        assert self.sock is not None
        chunks: list[bytes] = []
        self.sock.settimeout(self.timeout)
        while True:
            try:
                chunk = self.sock.recv(buffer_size)
            except socket.timeout:
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
            logger.error("Incomplete or no JSON response received from Blender")
            raise

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Blender")
        payload: Dict[str, Any] = {"type": command_type, "params": params or {}}
        assert self.sock is not None
        try:
            self.sock.sendall(json.dumps(payload).encode("utf-8"))
            data = self._receive_full_response()
            return json.loads(data.decode("utf-8"))
        except Exception:
            self.sock = None
            logger.exception("Error while sending command to Blender")
            raise


_blender_connection: Optional[BlenderConnection] = None


def get_blender_connection() -> BlenderConnection:
    global _blender_connection
    if _blender_connection is not None:
        return _blender_connection
    conn = BlenderConnection()
    if not conn.connect():
        raise ConnectionError("Could not connect to Blender. Ensure the Blender addon is running.")
    _blender_connection = conn
    return _blender_connection


@asynccontextmanager
async def server_lifespan(server: "Any") -> AsyncIterator[Dict[str, Any]]:
    try:
        try:
            get_blender_connection()
        except Exception:
            logger.debug("Blender not reachable at startup; continuing without Blender")
        yield {}
    finally:
        global _blender_connection
        if _blender_connection:
            try:
                _blender_connection.disconnect()
            except Exception:
                logger.exception("Error while disconnecting Blender connection during shutdown")
            _blender_connection = None


__all__ = ["BlenderConnection", "get_blender_connection", "server_lifespan"]

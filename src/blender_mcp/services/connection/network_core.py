"""Network core logic factored out from network.py.

This module contains a small, testable orchestrator that handles
connection selection (core vs socket), sending commands and receiving
full responses via ChunkedJSONReassembler. The public API mirrors the
previous `BlenderConnectionNetwork` surface but is easier to unit test.
"""

from __future__ import annotations

import json
import logging
import socket
from typing import Any, Dict, List, Optional, Type

from .reassembler import ChunkedJSONReassembler

logger = logging.getLogger(__name__)


# Explicit annotation so static analyzers know this name may be a type or None
CoreBlenderConnection: Optional[Type[Any]] = None
try:
    from ...connection_core import BlenderConnection as CoreBlenderConnection  # type: ignore
except Exception:
    CoreBlenderConnection = None  # type: ignore


class NetworkCore:
    """Orchestrates network transport using either the CoreBlenderConnection
    implementation (if available) or a raw socket + ChunkedJSONReassembler.

    Methods:
        connect(), disconnect(), receive_full_response(), send_command()
    """

    # Instance attribute annotations for static analyzers
    sock: Optional[socket.socket]
    _core: Optional[Any]

    def __init__(self, host: str = "localhost", port: int = 9876, *, socket_factory: Optional[Any] = None) -> None:
        self.host = host
        self.port = port
        self.sock = None
        self._core = None
        self._socket_factory = socket_factory  # optional override for raw socket creation

    def connect(self) -> bool:
        # If a socket factory is injected, prefer raw socket path (skip core)
        if self._socket_factory is None and CoreBlenderConnection is not None:
            if self._core is not None:
                return True
            try:
                self._core = CoreBlenderConnection(self.host, self.port)
                try:
                    ok = self._core.connect()
                except Exception:
                    ok = False
                if ok:
                    return True
                self._core = None
                return False
            except Exception:
                logger.exception("CoreBlenderConnection failed to init for %s:%s", self.host, self.port)
                self._core = None
                return False

        if self.sock:
            return True
        try:
            if self._socket_factory is not None:
                s = self._socket_factory()
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            self.sock = s
            logger.info("Connected to %s:%s", self.host, self.port)
            return True
        except Exception:
            self.sock = None
            logger.exception("Failed to connect to %s:%s", self.host, self.port)
            return False

    def disconnect(self) -> None:
        if self._core is not None:
            try:
                self._core.disconnect()
            except Exception:
                logger.exception("Error while disconnecting core connection")
            finally:
                self._core = None
            return

        if self.sock:
            try:
                self.sock.close()
            except Exception:
                logger.exception("Error while closing socket")
            finally:
                self.sock = None

    def receive_full_response(self, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
        if self._core is not None:
            return self._core._receive_full_response(buffer_size=buffer_size)  # type: ignore[attr-defined]

        if not self.sock:
            raise ConnectionError("Not connected")
        re = ChunkedJSONReassembler()
        self.sock.settimeout(timeout)
        chunks: List[bytes] = []
        try:
            while True:
                chunk = self.sock.recv(buffer_size)
                if not chunk:
                    break
                re.feed(chunk)
                msgs = re.pop_messages()
                if msgs:
                    return msgs[0]
                chunks.append(chunk)
        except socket.timeout:
            logger.warning("Socket timeout during receive_full_response")
            raise
        except Exception:
            logger.exception("Error while receiving data")
            raise

        joined = b"".join(chunks)
        if joined:
            try:
                return json.loads(joined.decode("utf-8"))
            except Exception:
                logger.debug("fallback JSON parse of joined chunks failed")

        raise ConnectionError("No data received")

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        # Prefer core implementation if available
        if self._core is not None:
            resp = self._core.send_command(command_type, params)  # type: ignore[attr-defined]
            # Use duck-typing to avoid static-analyzer warnings when the
            # core implementation is statically typed as a mapping.
            if hasattr(resp, "get"):
                # mypy/Pylance can't always infer this as a Mapping; silence
                # with a narrow assignment while keeping runtime-safety.
                r = resp  # type: ignore[assignment]
                if r.get("status") == "error":
                    raise RuntimeError(r.get("message", "error from peer"))
                return r.get("result", resp)
            return resp

        if not self.sock and not self.connect():
            raise ConnectionError("Not connected")
        cmd: Dict[str, Any] = {"type": command_type, "params": params or {}}
        data = (json.dumps(cmd) + "\n").encode("utf-8")
        try:
            assert self.sock is not None
            self.sock.sendall(data)
            resp = self.receive_full_response()
            if hasattr(resp, "get"):
                r = resp  # type: ignore[assignment]
                if r.get("status") == "error":
                    raise RuntimeError(r.get("message", "error from peer"))
                return r.get("result", resp)
            return resp
        except Exception:
            self.sock = None
            logger.exception("send_command failed")
            raise


__all__ = ["NetworkCore"]

"""Network client helpers for services.connection.

Implements a small client wrapper using newline-delimited JSON for
short-lived request/response flows.
"""

from __future__ import annotations

import json
import logging
import socket
from typing import Any, Dict, List, Optional, cast

from .reassembler import ChunkedJSONReassembler

# If available, prefer the canonical connection implementation for runtime
# compatibility. This lets higher-level services reuse the same connection
# logic while tests can still exercise the socket-level helpers.
try:
    from ...connection_core import BlenderConnection as CoreBlenderConnection  # type: ignore
except Exception:
    CoreBlenderConnection = None  # type: ignore

logger = logging.getLogger(__name__)


class BlenderConnectionNetwork:
    """Network-capable BlenderConnection using newline-delimited JSON.

    Small client wrapper with blocking methods suitable for short-lived
    request/response flows.
    """

    def __init__(self, host: str = "localhost", port: int = 9876) -> None:
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        # runtime-held core connection (when available); intentionally
        # un-annotated to avoid static-analysis issues when CoreBlenderConnection
        # isn't importable in some environments (tests/mock setups).
        self._core = None

    def connect(self) -> bool:
        # If a core connection implementation is available, use it.
        if CoreBlenderConnection is not None:
            if self._core is not None:
                return True
            try:
                # Instantiate the core connection and ensure it is actually connected.
                self._core = CoreBlenderConnection(self.host, self.port)
                try:
                    ok = self._core.connect()
                except Exception:
                    ok = False
                if ok:
                    return True
                # Core failed to connect; clear and signal failure so callers can
                # fall back to socket path or handle as appropriate.
                self._core = None
                return False
            except Exception:
                logger.exception("CoreBlenderConnection failed to init for %s:%s", self.host, self.port)
                self._core = None
                return False

        if self.sock:
            return True
        try:
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

    def receive_full_response(
        self, buffer_size: int = 8192, timeout: float = 15.0
    ) -> Any:
        if self._core is not None:
            # delegate to core implementation which handles full-response
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

    def send_command(
        self, command_type: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        # Prefer core implementation if available
        if self._core is not None:
            resp = self._core.send_command(command_type, params)
            # Maintain the same unwrapping semantics as the socket-based path:
            if isinstance(resp, dict):
                r = cast(Dict[str, Any], resp)
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
            # Narrow the type for Pylance/mypy: we expect a mapping-like response
            # for the typical request/response flow. Use a typed cast so `.get`
            # overloads are resolved and static analyzers stop complaining.
            if isinstance(resp, dict):
                r = cast(Dict[str, Any], resp)
                if r.get("status") == "error":
                    raise RuntimeError(r.get("message", "error from peer"))
                return r.get("result", resp)
            return resp
        except Exception:
            self.sock = None
            logger.exception("send_command failed")
            raise


__all__ = ["BlenderConnectionNetwork"]

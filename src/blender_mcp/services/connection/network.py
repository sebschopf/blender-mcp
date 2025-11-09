"""Network client helpers for services.connection.

Implements a small client wrapper using newline-delimited JSON for
short-lived request/response flows.
"""

from __future__ import annotations

import json
import logging
import socket
from typing import Any, Dict, List, Optional

from .reassembler import ChunkedJSONReassembler

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

    def connect(self) -> bool:
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
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected")
        cmd: Dict[str, Any] = {"type": command_type, "params": params or {}}
        data = (json.dumps(cmd) + "\n").encode("utf-8")
        try:
            assert self.sock is not None
            self.sock.sendall(data)
            resp = self.receive_full_response()
            if isinstance(resp, dict) and resp.get("status") == "error":
                raise RuntimeError(resp.get("message", "error from peer"))
            return resp.get("result", resp) if isinstance(resp, dict) else resp
        except Exception:
            self.sock = None
            logger.exception("send_command failed")
            raise


__all__ = ["BlenderConnectionNetwork"]

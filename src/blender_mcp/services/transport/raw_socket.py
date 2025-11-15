from __future__ import annotations

import json
import logging
import socket
import time
from typing import Any, Dict, Optional

from blender_mcp.services.connection.receiver import ResponseReceiver

logger = logging.getLogger(__name__)


class RawSocketTransport:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        socket_factory: Optional[Any] = None,
        retries: int = 1,
        backoff: float = 0.1,
    ) -> None:
        self.host = host
        self.port = port
        self._socket_factory = socket_factory
        self.sock: Optional[socket.socket] = None
        self._receiver = ResponseReceiver()
        # retry behavior on transient send/connect failures
        self.retries = int(retries)
        self.backoff = float(backoff)

    def connect(self) -> bool:
        if self.sock:
            return True
        try:
            if self._socket_factory is not None:
                s = self._socket_factory()
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            self.sock = s
            logger.info("Connected (raw) to %s:%s", self.host, self.port)
            return True
        except Exception:
            self.sock = None
            logger.exception("RawSocketTransport failed to connect to %s:%s", self.host, self.port)
            return False

    def disconnect(self) -> None:
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                logger.exception("Error while closing raw socket")
            finally:
                self.sock = None

    def receive_full_response(self, *, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
        if not self.sock:
            raise ConnectionError("Not connected")
        return self._receiver.receive_one(self.sock, buffer_size=buffer_size, timeout=timeout)

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        cmd: Dict[str, Any] = {"type": command_type, "params": params or {}}
        data = (json.dumps(cmd) + "\n").encode("utf-8")

        last_exc: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            if not self.sock and not self.connect():
                last_exc = ConnectionError("Not connected")
                # wait before retrying, but skip sleep on last attempt
                if attempt < self.retries:
                    time.sleep(self.backoff * (2 ** attempt))
                continue

            try:
                assert self.sock is not None
                self.sock.sendall(data)
                return self.receive_full_response()
            except Exception as exc:  # pragma: no cover - hard to hit all socket errors in tests
                logger.warning("RawSocketTransport send attempt %s failed: %s", attempt + 1, exc)
                # reset socket and retry if attempts remain
                try:
                    if self.sock:
                        self.sock.close()
                except Exception:
                    logger.debug("Error closing socket after failed send")
                finally:
                    self.sock = None

                last_exc = exc
                if attempt < self.retries:
                    time.sleep(self.backoff * (2 ** attempt))
                    continue
                logger.exception("RawSocketTransport send_command failed after %s attempts", self.retries + 1)
                raise last_exc

        # If we exit the retry loop without sending (e.g. connect() always failed),
        # raise the last seen exception to signal failure to the caller.
        if last_exc:
            raise last_exc
        raise ConnectionError("RawSocketTransport failed to send command")


__all__ = ["RawSocketTransport"]

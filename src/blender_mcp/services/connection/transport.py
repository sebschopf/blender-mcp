from __future__ import annotations

import json
import logging
import socket
from typing import Any, Dict, Optional, Protocol, Type, runtime_checkable
import time

from .receiver import ResponseReceiver

logger = logging.getLogger(__name__)


# Optional core connection import (deprecated path kept for compatibility)
CoreBlenderConnection: Optional[Type[Any]] = None
try:
    from ...connection_core import BlenderConnection as CoreBlenderConnection  # type: ignore
except Exception:
    CoreBlenderConnection = None  # type: ignore


@runtime_checkable
class Transport(Protocol):
    def connect(self) -> bool: ...  # noqa: E701
    def disconnect(self) -> None: ...  # noqa: E701
    def receive_full_response(self, *, buffer_size: int = 8192, timeout: float = 15.0) -> Any: ...  # noqa: E701
    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any: ...  # noqa: E701


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
                # wait before retrying
                time.sleep(self.backoff * (attempt + 1))
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
                    time.sleep(self.backoff * (attempt + 1))
                    continue
                logger.exception("RawSocketTransport send_command failed after %s attempts", self.retries + 1)
                raise last_exc


class CoreTransport:
    def __init__(self, host: str, port: int) -> None:
        if CoreBlenderConnection is None:
            raise RuntimeError("Core transport unavailable")
        self._core = CoreBlenderConnection(host, port)  # type: ignore[misc]

    def connect(self) -> bool:
        try:
            return bool(self._core.connect())  # type: ignore[no-any-return]
        except Exception:
            logger.exception("CoreTransport connect failed")
            return False

    def disconnect(self) -> None:
        try:
            self._core.disconnect()
        except Exception:
            logger.exception("CoreTransport disconnect failed")

    def receive_full_response(self, *, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
        # Core does not take timeout; preserve signature
        try:
            return self._core._receive_full_response(buffer_size=buffer_size)  # type: ignore[attr-defined]
        except Exception:
            logger.exception("CoreTransport receive_full_response failed")
            raise

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        try:
            return self._core.send_command(command_type, params)
        except Exception:
            logger.exception("CoreTransport send_command failed")
            raise


def select_transport(host: str, port: int, *, socket_factory: Optional[Any] = None) -> Transport:
    if socket_factory is not None:
        return RawSocketTransport(host, port, socket_factory=socket_factory)
    if CoreBlenderConnection is not None:
        try:
            return CoreTransport(host, port)
        except Exception:
            logger.debug("CoreTransport unavailable; falling back to raw socket")
    return RawSocketTransport(host, port)


__all__ = [
    "Transport",
    "RawSocketTransport",
    "CoreTransport",
    "select_transport",
]

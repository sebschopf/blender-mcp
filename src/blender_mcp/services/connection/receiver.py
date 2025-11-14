from __future__ import annotations

import json
import logging
import socket
from typing import Any

from .reassembler import ChunkedJSONReassembler

logger = logging.getLogger(__name__)


class ResponseReceiver:
    def __init__(self) -> None:
        self._re = ChunkedJSONReassembler()

    def receive_one(self, sock: socket.socket, *, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
        sock.settimeout(timeout)
        chunks: list[bytes] = []
        try:
            while True:
                chunk = sock.recv(buffer_size)
                if not chunk:
                    break
                self._re.feed(chunk)
                msgs = self._re.pop_messages()
                if msgs:
                    return msgs[0]
                chunks.append(chunk)
        except socket.timeout:
            logger.warning("Socket timeout in ResponseReceiver")
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


__all__ = ["ResponseReceiver"]

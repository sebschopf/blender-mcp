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
        """Receive a single JSON message from `sock`.

        This method accumulates bytes and uses `ChunkedJSONReassembler` to
        extract newline-delimited JSON objects. It enforces a maximum buffer
        size to avoid unbounded memory growth and treats socket timeouts as
        a transient error raised to the caller.

        Returns the first complete JSON-decoded object received.
        """

        sock.settimeout(timeout)
        chunks: list[bytes] = []
        max_size = 10 * 1024 * 1024  # 10 MiB default safety cap

        try:
            while True:
                chunk = sock.recv(buffer_size)
                if not chunk:
                    break
                chunks.append(chunk)
                # feed into reassembler and attempt to pop messages
                try:
                    self._re.feed(chunk)
                except Exception:
                    logger.exception("Error feeding reassembler")
                    raise

                # safety: avoid unbounded buffer growth
                buf_len = len(self._re._buffer)  # module-local access; intentional
                if buf_len > max_size:
                    logger.error("Incoming message exceeds max allowed size (%d bytes)", buf_len)
                    raise ConnectionError("Incoming message too large")

                msgs = self._re.pop_messages()
                if msgs:
                    # return the first complete message; remaining bytes stay in buffer
                    return msgs[0]

        except socket.timeout:
            logger.warning("Socket timeout in ResponseReceiver")
            raise
        except Exception:
            logger.exception("Error while receiving data")
            raise

        # No more data available from socket; try a last-ditch parse of joined chunks
        joined = b"".join(chunks)
        if joined:
            try:
                return json.loads(joined.decode("utf-8"))
            except Exception:
                logger.debug("fallback JSON parse of joined chunks failed")

        raise ConnectionError("No data received")


__all__ = ["ResponseReceiver"]

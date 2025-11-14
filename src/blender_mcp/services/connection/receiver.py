from __future__ import annotations

import json
import logging
import socket
import os
from typing import Any

from .reassembler import ChunkedJSONReassembler

logger = logging.getLogger(__name__)


class ResponseReceiver:
    def __init__(self, *, max_message_size: int | None = None) -> None:
        """Create a ResponseReceiver.

        Args:
            max_message_size: safety cap in bytes to avoid unbounded buffer growth.
                If `None`, the environment variable `BLENDER_MCP_MAX_MESSAGE_SIZE`
                will be read (expected as integer bytes). If that is not set,
                a default of 10 MiB is used.
        """
        self._re = ChunkedJSONReassembler()
        if max_message_size is None:
            env_val = os.environ.get("BLENDER_MCP_MAX_MESSAGE_SIZE")
            try:
                self.max_message_size = int(env_val) if env_val is not None else 10 * 1024 * 1024
            except ValueError:
                # If the env var is malformed, fall back to the default and
                # log a warning.
                logger.warning(
                    "Invalid BLENDER_MCP_MAX_MESSAGE_SIZE=%r, using default 10MiB",
                    env_val,
                )
                self.max_message_size = 10 * 1024 * 1024
        else:
            self.max_message_size = int(max_message_size)
        # queue for messages already popped from the reassembler but not yet
        # returned to the caller (multi-message recv handling)
        self._pending: list[Any] = []

    def receive_one(self, sock: socket.socket, *, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
        """Receive a single JSON message from `sock`.

        This method accumulates bytes and uses `ChunkedJSONReassembler` to
        extract newline-delimited JSON objects. It enforces a maximum buffer
        size to avoid unbounded memory growth and treats socket timeouts as
        a transient error raised to the caller.

        Returns the first complete JSON-decoded object received.
        """

        sock.settimeout(timeout)
        # If we have pending messages from a previous recv, return them first
        if self._pending:
            return self._pending.pop(0)

        # Otherwise, check if the underlying reassembler currently contains
        # complete messages (e.g., were popped by a prior feed); if so,
        # prime the pending queue and return the first.
        try:
            msgs = self._re.pop_messages()
        except Exception:
            logger.exception("Error popping messages from reassembler")
            msgs = []
        if msgs:
            # keep subsequent messages for later calls
            if len(msgs) > 1:
                self._pending.extend(msgs[1:])
            return msgs[0]

        chunks: list[bytes] = []

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
                if buf_len > self.max_message_size:
                    logger.error(
                        "Incoming message exceeds max allowed size (%d bytes) > %d",
                        buf_len,
                        self.max_message_size,
                    )
                    raise ConnectionError("Incoming message too large")

                msgs = self._re.pop_messages()
                if msgs:
                    # if multiple messages arrived in this single feed, queue
                    # the rest for subsequent calls and return the first now
                    if len(msgs) > 1:
                        self._pending.extend(msgs[1:])
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

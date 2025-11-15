from __future__ import annotations

import json
import logging
import os
import socket
from collections import deque
from typing import Any, Optional

from .reassembler import ChunkedJSONReassembler

logger = logging.getLogger(__name__)

# Default maximum message size: 10 MiB
DEFAULT_MAX_MESSAGE_SIZE = 10 * 1024 * 1024


class ResponseReceiver:
    """Receives and parses JSON messages from a socket.

    This receiver maintains internal state to handle multi-message buffering.
    When a single socket recv() call returns multiple complete JSON messages,
    they are queued internally and returned one at a time on subsequent
    receive_one() calls.

    Important: Because of this stateful buffering behavior, ResponseReceiver
    instances should not be shared across different sockets or connection
    contexts. Each socket connection should have its own ResponseReceiver
    instance to avoid mixing messages from different sources.
    """

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
                self.max_message_size = int(env_val) if env_val is not None else DEFAULT_MAX_MESSAGE_SIZE
            except ValueError:
                # If the env var is malformed, fall back to the default and
                # log a warning.
                logger.warning(
                    "Invalid BLENDER_MCP_MAX_MESSAGE_SIZE=%r, using default 10MiB",
                    env_val,
                )
                self.max_message_size = DEFAULT_MAX_MESSAGE_SIZE
        else:
            self.max_message_size = int(max_message_size)
        # queue for messages already popped from the reassembler but not yet
        # returned to the caller (multi-message recv handling)
        self._pending: deque[Any] = deque()

    def _pop_pending_or_reassembler(self) -> Optional[Any]:
        """Return a pending message or first available message from reassembler.

        Separated to reduce the complexity of `receive_one` and make each
        step easier to reason about and test.
        """
        if self._pending:
            return self._pending.popleft()

        try:
            msgs = self._re.pop_messages()
        except Exception:
            logger.exception("Error popping messages from reassembler")
            return None

        if msgs:
            if len(msgs) > 1:
                self._pending.extend(msgs[1:])
            return msgs[0]

        return None

    def _feed_and_check(self, sock: socket.socket, buffer_size: int) -> Optional[Any]:
        """Read chunks from `sock`, feed the reassembler and return a message if any.

        Raises socket.timeout or other exceptions from `recv` up to the caller.
        """
        chunks: list[bytes] = []
        while True:
            chunk = sock.recv(buffer_size)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                self._re.feed(chunk)
            except Exception:
                logger.exception("Error feeding reassembler")
                raise

            buf_len = self._re.get_buffer_size()
            if buf_len > self.max_message_size:
                logger.error(
                    "Incoming message exceeds max allowed size (%d bytes) > %d",
                    buf_len,
                    self.max_message_size,
                )
                raise ConnectionError("Incoming message too large")

            msgs = self._re.pop_messages()
            if msgs:
                if len(msgs) > 1:
                    self._pending.extend(msgs[1:])
                return msgs[0]

        # No more data; return joined bytes for potential fallback parse
        return b"".join(chunks)

    def _fallback_parse(self, joined: bytes) -> Optional[Any]:
        if not joined:
            return None
        try:
            return json.loads(joined.decode("utf-8"))
        except Exception:
            logger.debug("fallback JSON parse of joined chunks failed")
            return None

    def receive_one(self, sock: socket.socket, *, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
        """Receive a single JSON message from `sock`.

        If multiple messages arrive in a single recv() call, they are queued
        internally and returned one at a time on subsequent calls. This allows
        efficient handling of batched messages while maintaining a simple
        single-message API.

        This implementation delegates most work to small helpers to keep
        cognitive complexity low while preserving the original behavior.

        Args:
            sock: The socket to receive data from.
            buffer_size: Number of bytes to request in each recv() call.
            timeout: Socket timeout in seconds.

        Returns:
            A single decoded JSON message (dict or list).

        Raises:
            socket.timeout: If no data arrives within the timeout period.
            ConnectionError: If the message exceeds max_message_size or no data is received.
        """

        sock.settimeout(timeout)

        # Fast-path: pending or already-reassembled messages
        res = self._pop_pending_or_reassembler()
        if res is not None:
            return res

        try:
            read_res = self._feed_and_check(sock, buffer_size)
        except socket.timeout:
            logger.warning("Socket timeout in ResponseReceiver")
            raise
        except Exception:
            logger.exception("Error while receiving data")
            raise

        # If `_feed_and_check` returned a JSON-decoded object, return it
        if isinstance(read_res, (dict, list)):
            return read_res

        # Otherwise, `read_res` is the joined bytes; try fallback parse
        parsed = self._fallback_parse(read_res)  # type: ignore[arg-type]
        if parsed is not None:
            return parsed

        raise ConnectionError("No data received")


__all__ = ["ResponseReceiver"]

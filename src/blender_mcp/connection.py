"""Chunked JSON reassembly and a small, testable BlenderConnection helper.

The real Blender addon/socket protocol uses chunked JSON messages. To
keep the code testable without opening real sockets, this module provides
a `ChunkedJSONReassembler` that accepts arbitrary bytes and yields
complete JSON objects whenever a delimiter (newline) completes a
message. A lightweight `BlenderConnection` wraps the reassembler and
offers convenience methods used by higher-level server code.

Design notes:
- Messages are newline-delimited JSON (\n). Partial chunks are buffered.
- Parsing errors raise ValueError so callers can decide how to recover.
"""
from __future__ import annotations

import json
import logging
import socket
from typing import Any, Dict, Generator, List, Optional

logger = logging.getLogger(__name__)


class ChunkedJSONReassembler:
    """Accumulate bytes and extract newline-delimited JSON objects.

    This class is intentionally small and deterministic to make unit
    testing straightforward.
    """

    def __init__(self, delimiter: bytes = b"\n") -> None:
        self._buffer = bytearray()
        self.delimiter = delimiter

    def feed(self, data: bytes) -> None:
        """Feed raw bytes into the reassembler."""
        if not data:
            return
        self._buffer.extend(data)
        logger.debug("fed %d bytes, buffer now %d bytes", len(data), len(self._buffer))

    def pop_messages(self) -> List[Any]:
        """Return a list of fully reassembled JSON objects.

        Any trailing partial chunk is kept in the buffer for later.
        Raises ValueError if a completed chunk is not valid JSON.
        """
        messages: List[Any] = []
        delim = self.delimiter

        while True:
            idx = self._buffer.find(delim)
            if idx == -1:
                break
            chunk = bytes(self._buffer[:idx])
            # remove chunk + delimiter from buffer
            del self._buffer[: idx + len(delim)]
            if not chunk:
                # skip empty lines
                continue
            try:
                obj = json.loads(chunk.decode("utf-8"))
            except Exception as e:
                logger.exception("failed to parse JSON chunk: %r", chunk)
                raise ValueError("invalid JSON chunk") from e
            messages.append(obj)

        return messages


__all__ = ["ChunkedJSONReassembler", "BlenderConnection"]


# Backwards-compatible network-capable BlenderConnection used by higher-level
# code and tests. It reuses the ChunkedJSONReassembler for parsing incoming
# newline-delimited JSON messages.


class BlenderConnectionNetwork:
    """Network-capable BlenderConnection compatible with existing tests.

    This class exposes a similar API to the previous implementation used in
    the repository: connect(), disconnect(), send_command(). It uses the
    ChunkedJSONReassembler to accumulate and parse newline-delimited JSON
    responses from the socket.
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
            logger.info("Connected to Blender at %s:%s", self.host, self.port)
            return True
        except Exception:
            self.sock = None
            logger.exception("Failed to connect to Blender at %s:%s", self.host, self.port)
            return False

    def disconnect(self) -> None:
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                logger.exception("Error while closing Blender socket")
            finally:
                self.sock = None

    def receive_full_response(self, buffer_size: int = 8192, timeout: float = 15.0) -> Dict[str, Any]:
        """Read from the socket until at least one full JSON message is parsed.

        Returns the parsed JSON object (the first message). Raises on errors.
        """
        if not self.sock:
            raise ConnectionError("Not connected")

        re = ChunkedJSONReassembler()
        self.sock.settimeout(timeout)
        chunks: List[bytes] = []

        try:
            while True:
                chunk = self.sock.recv(buffer_size)
                if not chunk:
                    # connection closed
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
            logger.exception("Error while receiving data from Blender")
            raise

        # If we reach here, the connection closed; try to parse whatever we have.
        # Some servers do not send a trailing newline; try to parse the joined
        # bytes as raw JSON as a fallback.
        joined = b"".join(chunks)
        if joined:
            try:
                return json.loads(joined.decode("utf-8"))
            except Exception:
                # fall-through to error below
                logger.debug("fallback JSON parse of joined chunks failed")

        raise ConnectionError("No data received from Blender")

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Blender")

        cmd = {"type": command_type, "params": params or {}}
        data = (json.dumps(cmd) + "\n").encode("utf-8")
        try:
            assert self.sock is not None
            self.sock.sendall(data)
            resp = self.receive_full_response()
            if isinstance(resp, dict) and resp.get("status") == "error":
                raise RuntimeError(resp.get("message", "error from blender"))
            return resp.get("result", resp) if isinstance(resp, dict) else resp
        except Exception:
            # Invalidate the socket so callers will reconnect next time
            self.sock = None
            logger.exception("send_command failed")
            raise


class BlenderConnection:
    """Compatibility wrapper exposing both reassembler-style helpers and
    the network-capable API depending on how it's constructed.

    Usage:
    - `BlenderConnection()` -> lightweight reassembler helper (feed_bytes, get_messages, iter_messages_from_chunks)
    - `BlenderConnection(host, port)` -> network-capable object (connect, send_command, receive_full_response)
    """

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        self._re = ChunkedJSONReassembler()
        # Explicitly annotate _net as optional so static checkers know it may be None
        self._net: Optional[BlenderConnectionNetwork] = None
        if host is not None and port is not None:
            self._net = BlenderConnectionNetwork(host, port)

    # reassembler-style API
    def feed_bytes(self, data: bytes) -> None:
        self._re.feed(data)

    def get_messages(self) -> List[Any]:
        return self._re.pop_messages()

    def iter_messages_from_chunks(self, chunks: Generator[bytes, None, None]) -> Generator[Any, None, None]:
        for c in chunks:
            self.feed_bytes(c)
            for msg in self.get_messages():
                yield msg

    # network-style API: delegate to underlying network object
    def connect(self) -> bool:
        if not self._net:
            raise TypeError("network methods are unavailable when host/port are not provided")
        return self._net.connect()

    def disconnect(self) -> None:
        if not self._net:
            raise TypeError("network methods are unavailable when host/port are not provided")
        return self._net.disconnect()

    def receive_full_response(self, buffer_size: int = 8192, timeout: float = 15.0) -> Dict[str, Any]:
        if not self._net:
            raise TypeError("network methods are unavailable when host/port are not provided")
        return self._net.receive_full_response(buffer_size=buffer_size, timeout=timeout)

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self._net:
            raise TypeError("network methods are unavailable when host/port are not provided")
        return self._net.send_command(command_type, params)




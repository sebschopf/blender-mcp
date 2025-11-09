from __future__ import annotations

"""Clean, testable connection helpers for BlenderMCP.

This module provides small, synchronous helpers that are straightforward
to test with ``socket.socketpair()``. It supports two framing styles and
exposes a compatibility facade used in tests.
"""

import json
import logging
import socket
import struct
from typing import Any, Dict, Generator, List, Optional

logger = logging.getLogger(__name__)


class ChunkedJSONReassembler:
    """Accumulate bytes and extract newline-delimited JSON objects.

    Messages are delimited by a byte sequence (default: ``b"\n"``).
    Completed JSON objects are returned as Python objects.
    """

    def __init__(self, delimiter: bytes = b"\n") -> None:
        self._buffer = bytearray()
        self.delimiter = delimiter

    def feed(self, data: bytes) -> None:
        if not data:
            return
        self._buffer.extend(data)
        logger.debug("fed %d bytes, buffer now %d bytes", len(data), len(self._buffer))

    def pop_messages(self) -> List[Any]:
        messages: List[Any] = []
        delim = self.delimiter

        while True:
            idx = self._buffer.find(delim)
            if idx == -1:
                break
            chunk = bytes(self._buffer[:idx])
            del self._buffer[: idx + len(delim)]
            if not chunk:
                continue
            try:
                obj = json.loads(chunk.decode("utf-8"))
            except Exception as exc:
                logger.exception("failed to parse JSON chunk: %r", chunk)
                raise ValueError("invalid JSON chunk") from exc
            messages.append(obj)

        return messages


class LengthPrefixedReassembler:
    """Reassemble messages framed with a 4-byte big-endian length header.

    The header is an unsigned 32-bit big-endian integer describing the
    following payload length in bytes.
    """

    HEADER_FMT = ">I"
    HEADER_SIZE = struct.calcsize(HEADER_FMT)

    def __init__(self) -> None:
        self._buffer = bytearray()

    def feed(self, data: bytes) -> None:
        if not data:
            return
        self._buffer.extend(data)

    def pop_messages(self) -> List[bytes]:
        msgs: List[bytes] = []
        while True:
            if len(self._buffer) < self.HEADER_SIZE:
                break
            hdr = bytes(self._buffer[: self.HEADER_SIZE])
            length = struct.unpack(self.HEADER_FMT, hdr)[0]
            if len(self._buffer) < self.HEADER_SIZE + length:
                break
            start = self.HEADER_SIZE
            payload = bytes(self._buffer[start : start + length])
            del self._buffer[: self.HEADER_SIZE + length]
            msgs.append(payload)
        return msgs


class SocketBlenderConnection:
    """Socket-injected connection using length-prefixed frames.

    Tests pass a socketpair endpoint into ``BlenderConnection(sock)``; this
    class implements the send/receive semantics for that mode.
    """

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock
        self._re = LengthPrefixedReassembler()
        # pending messages extracted from the reassembler but not yet
        # returned to callers (used when multiple frames arrive together)
        self._pending: List[bytes] = []

    def send(self, obj: Any) -> None:
        payload = json.dumps(obj, separators=(",", ":")).encode("utf-8")
        frame = struct.pack(LengthPrefixedReassembler.HEADER_FMT, len(payload)) + payload
        self._sock.sendall(frame)

    def receive(self, timeout: Optional[float] = None) -> Any:
        orig = self._sock.gettimeout()
        try:
            self._sock.settimeout(timeout)
            # fast path: check any previously buffered pending frames
            if self._pending:
                payload = self._pending.pop(0)
                return json.loads(payload.decode("utf-8"))

            msgs = self._re.pop_messages()
            if msgs:
                # if multiple messages arrived, keep the extras for later
                if len(msgs) > 1:
                    self._pending.extend(msgs[1:])
                return json.loads(msgs[0].decode("utf-8"))

            while True:
                try:
                    chunk = self._sock.recv(4096)
                except socket.timeout:
                    raise TimeoutError("receive timed out")
                if not chunk:
                    raise ConnectionError("socket closed")
                self._re.feed(chunk)
                msgs = self._re.pop_messages()
                if msgs:
                    if len(msgs) > 1:
                        self._pending.extend(msgs[1:])
                    return json.loads(msgs[0].decode("utf-8"))
        finally:
            self._sock.settimeout(orig)


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

    def receive_full_response(self, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
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


class BlenderConnection:
    """Compatibility façade.

    Modes:
    - BlenderConnection(sock) -> socket-injected length-prefixed framing (send/receive)
    - BlenderConnection(host, port) -> network client (connect/send_command)
    - BlenderConnection() -> reassembler helper (feed_bytes/get_messages)
    """

    def __init__(self, *args: object) -> None:
        # socket-injected mode
        if len(args) == 1 and isinstance(args[0], socket.socket):
            self._mode = "socket"
            self._socket_conn = SocketBlenderConnection(args[0])
            return

        # network mode: host, port
        if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], int):
            self._mode = "network"
            self._net = BlenderConnectionNetwork(args[0], args[1])
            return

        # default: reassembler
        self._mode = "reassembler"
        self._re = ChunkedJSONReassembler()

    # reassembler API
    def feed_bytes(self, data: bytes) -> None:
        if self._mode != "reassembler":
            raise TypeError("feed_bytes is only available in reassembler mode")
        self._re.feed(data)

    def get_messages(self) -> List[Any]:
        if self._mode != "reassembler":
            raise TypeError("get_messages is only available in reassembler mode")
        return self._re.pop_messages()

    def iter_messages_from_chunks(self, chunks: Generator[bytes, None, None]) -> Generator[Any, None, None]:
        if self._mode != "reassembler":
            raise TypeError("iter_messages_from_chunks is only available in reassembler mode")
        for c in chunks:
            self.feed_bytes(c)
            for msg in self.get_messages():
                yield msg

    # socket API
    def send(self, obj: Any) -> None:
        if self._mode != "socket":
            raise TypeError("send is only available in socket mode")
        self._socket_conn.send(obj)

    def receive(self, timeout: Optional[float] = None) -> Any:
        if self._mode != "socket":
            raise TypeError("receive is only available in socket mode")
        return self._socket_conn.receive(timeout=timeout)

    # network API
    def connect(self) -> bool:
        if self._mode != "network":
            raise TypeError("connect is only available in network mode")
        return self._net.connect()

    def disconnect(self) -> None:
        if self._mode != "network":
            raise TypeError("disconnect is only available in network mode")
        return self._net.disconnect()

    def receive_full_response(self, buffer_size: int = 8192, timeout: float = 15.0) -> Dict[str, Any]:
        if self._mode != "network":
            raise TypeError("receive_full_response is only available in network mode")
        return self._net.receive_full_response(buffer_size=buffer_size, timeout=timeout)

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if self._mode != "network":
            raise TypeError("send_command is only available in network mode")
        return self._net.send_command(command_type, params)


__all__ = [
    "ChunkedJSONReassembler",
    "LengthPrefixedReassembler",
    "SocketBlenderConnection",
    "BlenderConnectionNetwork",
    "BlenderConnection",
]

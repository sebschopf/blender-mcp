"""Socket-backed connection for services.connection.

This module implements the socket-injected connection using
length-prefixed frames. It depends on the framing reassembler implemented
in :mod:`.framing`.
"""

from __future__ import annotations

import json
import socket
import struct
from typing import Any, List, Optional

from .framing import LengthPrefixedReassembler


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


__all__ = ["SocketBlenderConnection"]

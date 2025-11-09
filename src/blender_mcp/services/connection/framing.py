"""Framing helpers (length-prefixed) for services.connection.

This module implements a simple length-prefixed reassembler used by the
socket-backed connection.
"""

from __future__ import annotations

import struct
from typing import List


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


__all__ = ["LengthPrefixedReassembler"]

"""Reassembler helpers (newline-delimited JSON) for services.connection.

Implementation moved from the package-level internal module to make the
`services.connection` package self-contained (SOLID). This module
implements newline-delimited JSON reassembly.
"""

from __future__ import annotations

import json
import logging
from typing import Any, List

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


__all__ = ["ChunkedJSONReassembler"]

"""Facade module exposing the high-level BlenderConnection.

Provides a multi-mode helper that can be used in three ways:
- socket-injected length-prefixed framing
- network client (host, port)
- reassembler helper (feed_bytes/get_messages)
"""

from __future__ import annotations

from typing import Any, Dict, Generator, List, Optional

from .network import BlenderConnectionNetwork
from .reassembler import ChunkedJSONReassembler
from .socket_conn import SocketBlenderConnection


class BlenderConnection:
    """Compatibility façade.

    Modes:
    - BlenderConnection(sock) -> socket-injected length-prefixed framing (send/receive)
    - BlenderConnection(host, port) -> network client (connect/send_command)
    - BlenderConnection() -> reassembler helper (feed_bytes/get_messages)
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        # socket-injected mode
        if len(args) == 1 and hasattr(args[0], "recv"):
            self._mode = "socket"
            self._socket_conn = SocketBlenderConnection(args[0])  # type: ignore[arg-type]
            return

        # network mode: host, port
        if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], int):
            self._mode = "network"
            self._net = BlenderConnectionNetwork(args[0], args[1], socket_factory=kwargs.get("socket_factory"))
            return

        # network mode with defaults but socket_factory kw provided
        if not args and "socket_factory" in kwargs:
            self._mode = "network"
            self._net = BlenderConnectionNetwork(socket_factory=kwargs.get("socket_factory"))
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


__all__ = ["BlenderConnection"]

"""Network core logic factored out from network.py.

This module contains a small, testable orchestrator that handles
transport selection and delegates to a concrete transport. The public
API mirrors the previous `BlenderConnectionNetwork` surface.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .transport import Transport, select_transport

logger = logging.getLogger(__name__)


class NetworkCore:
    """Orchestrates network transport via a selected Transport implementation."""

    _transport: Transport

    def __init__(self, host: str = "localhost", port: int = 9876, *, socket_factory: Optional[Any] = None) -> None:
        self.host = host
        self.port = port
        self._transport = select_transport(host, port, socket_factory=socket_factory)

    def connect(self) -> bool:
        return self._transport.connect()

    def disconnect(self) -> None:
        return self._transport.disconnect()

    def receive_full_response(self, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
        return self._transport.receive_full_response(buffer_size=buffer_size, timeout=timeout)

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._transport.send_command(command_type, params)


__all__ = ["NetworkCore"]

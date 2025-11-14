"""Network client helpers for services.connection.

Implements a small client wrapper using newline-delimited JSON for
short-lived request/response flows.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .network_core import NetworkCore
from .transport import Transport

logger = logging.getLogger(__name__)


class BlenderConnectionNetwork:
    """Compatibility façade for the network core.

    This class preserves the historical API but delegates all heavy lifting
    to :class:`NetworkCore` so the implementation is easier to test and
    maintain.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9876,
        *,
        socket_factory=None,
        transport: Optional[Transport] = None,
    ) -> None:
        self._core = NetworkCore(host=host, port=port, socket_factory=socket_factory, transport=transport)

    def connect(self) -> bool:
        return self._core.connect()

    def disconnect(self) -> None:
        return self._core.disconnect()

    def receive_full_response(self, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
        return self._core.receive_full_response(buffer_size=buffer_size, timeout=timeout)

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._core.send_command(command_type, params)


__all__ = ["BlenderConnectionNetwork"]

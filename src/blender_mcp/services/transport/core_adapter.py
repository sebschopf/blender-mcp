from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CoreTransport:
    """Adapter around the project-local core `BlenderConnection`.

    The adapter performs a lazy import of the canonical core implementation
    so that importing this module does not force the connection core to be
    resolved at package-import time (avoids import cycles in tests).
    """

    def __init__(self, host: str, port: int) -> None:
        try:
            # Lazy import: the Core BlenderConnection lives at a higher layer
            # in the package; import at runtime to avoid import-order issues.
            from ...connection_core import BlenderConnection as CoreBlenderConnection  # type: ignore

            self._core = CoreBlenderConnection(host, port)  # type: ignore[misc]
        except Exception:
            raise RuntimeError("Core transport unavailable")

    def connect(self) -> bool:
        try:
            return bool(self._core.connect())  # type: ignore[no-any-return]
        except Exception:
            logger.exception("CoreTransport connect failed")
            return False

    def disconnect(self) -> None:
        try:
            self._core.disconnect()
        except Exception:
            logger.exception("CoreTransport disconnect failed")

    def receive_full_response(self, *, buffer_size: int = 8192, timeout: float = 15.0) -> Any:
        # Core does not take timeout; preserve signature
        try:
            return self._core._receive_full_response(buffer_size=buffer_size)  # type: ignore[attr-defined]
        except Exception:
            logger.exception("CoreTransport receive_full_response failed")
            raise

    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        try:
            return self._core.send_command(command_type, params)
        except Exception:
            logger.exception("CoreTransport send_command failed")
            raise


__all__ = ["CoreTransport"]

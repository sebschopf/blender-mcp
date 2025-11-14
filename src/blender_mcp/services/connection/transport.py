from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from blender_mcp.services.transport import Transport
from blender_mcp.services.transport.raw_socket import RawSocketTransport
from blender_mcp.services.transport.core_adapter import CoreTransport

logger = logging.getLogger(__name__)


# Note: prefer lazy import of the core `BlenderConnection` to avoid
# import-order issues during tests and to keep the module import-safe.



# CoreTransport adapter extracted to `services.transport.core_adapter`.


def select_transport(host: str, port: int, *, socket_factory: Optional[Any] = None) -> Transport:
    if socket_factory is not None:
        return RawSocketTransport(host, port, socket_factory=socket_factory)
    # Try to use CoreTransport if the canonical core implementation is
    # importable. CoreTransport does a lazy import and raises RuntimeError
    # when the core is unavailable.
    try:
        t: Transport = CoreTransport(host, port)
        logger.debug("select_transport: using CoreTransport")
        return t
    except RuntimeError:
        logger.debug("CoreTransport unavailable; falling back to raw socket")
    # Fall back to raw transport
    t = RawSocketTransport(host, port, socket_factory=socket_factory)
    logger.debug("select_transport: using RawSocketTransport")
    return t


__all__ = [
    "Transport",
    "RawSocketTransport",
    "CoreTransport",
    "select_transport",
]


# Diagnostics removed: transport implementation now lives under services.transport.

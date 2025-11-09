"""Very small, import-safe helpers for unit tests.

This module provides a small but complete server façade used during the
refactor. It intentionally avoids importing Blender (`bpy`) at import
time and delegates handler logic to `blender_mcp.dispatcher`.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from .dispatcher import Dispatcher, register_default_handlers
from .endpoints import register_builtin_endpoints

logger = logging.getLogger(__name__)


def _process_bbox(
    bbox: Optional[list[float] | tuple[float, float, float]],
) -> Optional[list[int]]:
    if bbox is None:
        return None
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 3:
        raise ValueError("bbox must be a 3-tuple/list or None")
    vals = [float(x) for x in bbox]
    if any(v < 0 for v in vals):
        raise ValueError("bbox values must be non-negative")
    mx = max(vals)
    if mx == 0:
        raise ValueError("bbox max cannot be zero")
    factor = 100 if mx <= 1.0 else 50
    return [int(v * factor) for v in vals]


class BlenderMCPServer:
    """Tiny server façade used by tests and early refactor.

    The server lazily creates a `Dispatcher` and registers a small set of
    default handlers. It exposes `execute_command` which returns a JSON
    serializable dict matching the previous test contract.
    """

    def __init__(self) -> None:
        self._dispatcher: Optional[Dispatcher] = None

    def _ensure_dispatcher(self) -> None:
        if self._dispatcher is None:
            self._dispatcher = Dispatcher()
            register_default_handlers(self._dispatcher)
            # register ported endpoints (thin wrappers around services)
            register_builtin_endpoints(self._dispatcher.register)

    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command dict and return a response dict.

        Expected command shape: {"tool"|"type": <str>, "params": {...}}
        Returns {"status":"ok","handled":bool,...}
        """
        self._ensure_dispatcher()
        # use the normalized dispatch_command to get structured responses
        # _ensure_dispatcher guarantees _dispatcher is set at this point
        assert self._dispatcher is not None
        dispatcher = self._dispatcher
        resp = dispatcher.dispatch_command(command)
        if resp.get("status") == "success":
            return {"status": "ok", "handled": True, "result": resp.get("result")}

        # fallback echo behaviour expected by tests when handler is missing or errored
        return {"status": "ok", "handled": False, "echo": command}

    def _schedule_execute_wrapper(self, client: Any, command: Dict[str, Any]) -> None:
        result = self.execute_command(command)
        client.sendall(json.dumps(result).encode("utf-8"))


__all__ = ["_process_bbox", "BlenderMCPServer"]

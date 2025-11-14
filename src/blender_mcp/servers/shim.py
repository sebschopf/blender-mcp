"""Server shim moved into the `servers` package.

Relocated `server_shim.py` to `servers/shim.py` and adjusted imports.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from ..dispatchers.dispatcher import Dispatcher, register_default_handlers

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
    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        if not hasattr(self, "_dispatcher"):
            self._dispatcher = Dispatcher()
            register_default_handlers(self._dispatcher)

        tool = command.get("tool") or command.get("type")
        params = command.get("params", {})
        if tool:
            result = self._dispatcher.dispatch(tool, params)
            if result is not None:
                return {"status": "ok", "handled": True, "result": result}

        return {"status": "ok", "handled": False, "echo": command}

    def _schedule_execute_wrapper(self, client: Any, command: Dict[str, Any]) -> None:
        result = self.execute_command(command)
        client.sendall(json.dumps(result).encode("utf-8"))


__all__ = ["BlenderMCPServer", "_process_bbox"]

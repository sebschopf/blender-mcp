"""Service implementing execute_blender_code and a network helper.

This module demonstrates a pattern for endpoint porting:
- lazy import of `bpy` inside `execute_blender_code` so the package can be
  imported in CI/test environments without having Blender available.
- a small network wrapper `send_command_over_network` that uses the
  `BlenderConnectionNetwork` (kept testable via socket monkeypatching).
"""
from __future__ import annotations

import importlib
import logging
from typing import Any, Dict, Optional

from ..connection import BlenderConnectionNetwork

logger = logging.getLogger(__name__)


def execute_blender_code(params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a small piece of Python in Blender's context.

    params expected keys:
    - code: str — a Python snippet that may read/write `bpy` and may set a
      variable `result` to return a structured value.

    Returns a dict with status and result/message.
    """
    code = params.get("code")
    if not isinstance(code, str):
        return {"status": "error", "message": "missing or invalid 'code'"}

    try:
        # lazy import of bpy to keep module import safe
        bpy = importlib.import_module("bpy")
    except Exception:
        logger.debug("bpy not available (not running inside Blender)")
        return {"status": "error", "message": "Blender (bpy) not available"}

    # execute user code in a minimal namespace exposing only `bpy`
    local_ns: Dict[str, Any] = {}
    try:
        exec(code, {"bpy": bpy}, local_ns)
        return {"status": "success", "result": local_ns.get("result")}
    except Exception as e:
        logger.exception("error executing blender code")
        return {"status": "error", "message": str(e)}


def send_command_over_network(host: str, port: int, command_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Helper to send a command to Blender over TCP and return the result.

    This function constructs a `BlenderConnectionNetwork`, connects, sends
    the command and returns the command result. Tests can monkeypatch
    `socket.socket` so no real network is used.
    """
    conn = BlenderConnectionNetwork(host, port)
    if not conn.connect():
        raise ConnectionError(f"Could not connect to Blender at {host}:{port}")
    return conn.send_command(command_type, params or {})


__all__ = ["execute_blender_code", "send_command_over_network"]

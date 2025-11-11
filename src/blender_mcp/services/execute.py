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
import os
from typing import Any, Dict, Optional

from blender_mcp.dispatchers.dispatcher import Dispatcher
from blender_mcp.services.connection import BlenderConnectionNetwork

logger = logging.getLogger(__name__)

# Dedicated audit logger for execute_blender_code calls. Keep handler local so
# we don't change global logging configuration for consumers.
_audit_logger = logging.getLogger("blender_mcp.execute.audit")
if not _audit_logger.handlers:
    try:
        fh = logging.FileHandler("blender_mcp_execute.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        _audit_logger.addHandler(fh)
        _audit_logger.setLevel(logging.INFO)
    except Exception:
        # Fall back to no-file logging if filesystem not writable; don't crash.
        _audit_logger.addHandler(logging.NullHandler())


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

    # Audit the request (truncate code to reasonable length in logs)
    truncated = code[:200] + ("..." if len(code) > 200 else "")
    _audit_logger.info("execute_blender_code request: len=%d code=%s", len(code), truncated)

    # Dry-run env var (optional) — kept for testing/administrative use
    dry_run = os.getenv("BLENDER_MCP_EXECUTE_DRY_RUN", "0") == "1"

    try:
        # lazy import of bpy to keep module import safe
        bpy = importlib.import_module("bpy")
    except Exception:
        logger.debug("bpy not available (not running inside Blender)")
        _audit_logger.error("bpy not available; cannot execute code")
        return {"status": "error", "message": "Blender (bpy) not available"}

    # execute user code in a minimal namespace exposing only `bpy`
    local_ns: Dict[str, Any] = {}
    try:
        if dry_run:
            _audit_logger.info("dry-run: code not executed")
            return {"status": "ok", "message": "dry-run: code not executed (BLENDER_MCP_EXECUTE_DRY_RUN=1)"}

        exec(code, {"bpy": bpy}, local_ns)
        result = local_ns.get("result")
        _audit_logger.info("execute_blender_code succeeded: result=%s", repr(result))
        return {"status": "success", "result": result}
    except Exception as e:
        logger.exception("error executing blender code")
        _audit_logger.exception("execute_blender_code failed: %s", str(e))
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


def register_handlers(dispatcher: Dispatcher) -> None:
    """Register service handlers on a Dispatcher instance.

    This helper makes it easy to wire services into the dispatcher used by
    the running server or tests. It attempts to call `register(...,
    overwrite=True)` for idempotence and falls back if the older
    Dispatcher signature does not accept `overwrite`.
    """
    try:
        dispatcher.register("execute_blender_code", execute_blender_code, overwrite=True)  # type: ignore[arg-type]
    except TypeError:
        dispatcher.register("execute_blender_code", execute_blender_code)

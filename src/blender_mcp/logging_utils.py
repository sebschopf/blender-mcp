"""Small audit/logging helpers for blender_mcp.

Keep these minimal and test-friendly: they format an audit-friendly log
and emit at INFO for successful actions and WARN/ERROR for failures.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("blender_mcp.audit")


def log_action(source: str, action: str, params: Optional[Dict[str, Any]] = None, result: Optional[Any] = None) -> None:
    """Emit a structured audit message.

    This function is intentionally small so tests can monkeypatch or
    capture logs easily.
    """
    payload = {
        "source": source,
        "action": action,
        "params": params,
        "result": result,
    }
    logger.info("audit: %s", payload)

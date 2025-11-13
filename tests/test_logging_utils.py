from __future__ import annotations

import logging
from typing import Any, Dict

import pytest

from blender_mcp.logging_utils import log_action


def test_log_action_emits_info(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="blender_mcp.audit")
    log_action("unit", "test_event", {"a": 1}, {"ok": True})
    records = [r for r in caplog.records if r.name == "blender_mcp.audit"]
    assert records, "Aucun log capturé"
    rec = records[-1]
    assert rec.levelno == logging.INFO
    assert "audit:" in rec.getMessage()
    assert "test_event" in rec.getMessage()


def test_log_action_payload_shape(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="blender_mcp.audit")
    params: Dict[str, Any] = {"x": 2}
    result = {"value": 10}
    log_action("svc", "done", params, result)
    rec = [r for r in caplog.records if r.name == "blender_mcp.audit"][-1]
    msg = rec.getMessage()
    assert "svc" in msg and "done" in msg
    # Basic presence of serialized dict keys
    assert "'params': {'x': 2}" in msg
    assert "'result': {'value': 10}" in msg

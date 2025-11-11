from __future__ import annotations

from typing import Any, Dict, Optional

from blender_mcp.dispatchers.command_adapter import CommandAdapter
from blender_mcp.dispatchers.dispatcher import Dispatcher


def test_policy_allows_command() -> None:
    d = Dispatcher()

    d.register("ok", lambda params: {"ok": True}, overwrite=True)

    def policy_allow(cmd_type: str, params: Dict[str, Any]) -> Optional[str]:
        # allow everything
        return None

    adapter = CommandAdapter(d, policy_check=policy_allow)
    resp = adapter.dispatch_command({"type": "ok", "params": {}})
    assert resp["status"] == "success"


def test_policy_blocks_command() -> None:
    d = Dispatcher()

    d.register("danger", lambda params: {"ok": False}, overwrite=True)

    def policy_block(cmd_type: str, params: Dict[str, Any]) -> Optional[str]:
        return "not allowed"

    adapter = CommandAdapter(d, policy_check=policy_block)
    resp = adapter.dispatch_command({"type": "danger", "params": {}})
    assert resp["status"] == "error"
    assert "Blocked by policy" in resp["message"]

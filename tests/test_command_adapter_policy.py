from __future__ import annotations

from typing import Any, Dict, Optional

from blender_mcp.dispatchers.command_adapter import CommandAdapter
from blender_mcp.dispatchers.dispatcher import Dispatcher


def test_command_adapter_policy_blocks_and_allows() -> None:
    d = Dispatcher()

    def handler(params: Dict[str, object]):
        return {"ok": True, "params": params}

    d.register("foo", handler, overwrite=True)

    def policy_check(cmd_type: str, params: Dict[str, object]) -> Optional[str]:
        # block when param 'deny' is truthy
        if cmd_type == "foo" and params.get("deny"):
            return "explicit deny"
        return None

    adapter = CommandAdapter(d, policy_check=policy_check)

    res = adapter.dispatch_command({"type": "foo", "params": {}})
    assert res["status"] == "success"

    res2 = adapter.dispatch_command({"type": "foo", "params": {"deny": True}})
    assert res2["status"] == "error"
    assert "Blocked by policy" in res2["message"]


def test_dispatcher_dispatch_command_wires_policy() -> None:
    def policy_check(cmd_type: str, params: Dict[str, object]) -> Optional[str]:
        if cmd_type == "bar":
            return "nope"
        return None

    d = Dispatcher(policy_check=policy_check)

    def bar_handler(params: Dict[str, object]):
        return {"ok": True}

    d.register("bar", bar_handler, overwrite=True)

    res = d.dispatch_command({"type": "bar", "params": {}})
    assert res["status"] == "error"
    assert "Blocked by policy" in res["message"]


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


def test_dispatcher_policy_override_precedence() -> None:
    """La policy per-call doit primer sur la policy d'instance."""
    def policy_check(cmd_type: str, params: Dict[str, Any]) -> Optional[str]:
        if cmd_type == "bar":
            return "nope"
        return None

    d = Dispatcher(policy_check=policy_check)

    d.register("ok", lambda params: {"ok": True}, overwrite=True)

    # Override per-call permet de passer malgré la policy par défaut
    resp = d.dispatch_command({"type": "ok", "params": {}}, policy_check=lambda t, p: None)
    assert resp["status"] == "success"


def test_dispatcher_policy_runtime_update() -> None:
    """Changer la policy via setter doit s'appliquer immédiatement par défaut."""
    d = Dispatcher()
    d.register("ok", lambda params: {"ok": True}, overwrite=True)

    # Par défaut: pas de policy -> autorisé
    resp1 = d.dispatch_command({"type": "ok", "params": {}})
    assert resp1["status"] == "success"

    # Appliquer une policy deny via setter
    def deny_policy(cmd_type: str, params: Dict[str, Any]) -> Optional[str]:
        return "denied"

    d.set_policy_check(deny_policy)

    # Maintenant, sans override per-call, la commande doit être bloquée
    resp2 = d.dispatch_command({"type": "ok", "params": {}})
    assert resp2["status"] == "error"
    assert resp2.get("error_code") == "policy_denied"

    # Et avec un override per-call allow, ça doit passer
    resp3 = d.dispatch_command({"type": "ok", "params": {}}, policy_check=lambda t, p: None)
    assert resp3["status"] == "success"

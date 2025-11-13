from typing import Dict, Any

from blender_mcp.dispatchers.dispatcher import Dispatcher
from blender_mcp.dispatchers.strategies import HandlerResolutionStrategy, PolicyStrategy
from blender_mcp.dispatchers.policies import PolicyChecker


class CustomHandlerResolution(HandlerResolutionStrategy):
    def resolve(self, dispatcher: Dispatcher, name: str):  # type: ignore[override]
        # Force a synthetic handler for a specific name
        if name == "synthetic_handler":
            return lambda params: {"ok": True, "echo": params.get("x", 1)}
        return dispatcher._resolve_handler_or_service(name)


class CustomPolicyStrategy(PolicyStrategy):
    def check(self, checker: PolicyChecker | None, command: Dict[str, Any]):  # type: ignore[override]
        # Deny a specific command type regardless of checker
        if command.get("type") == "blocked_command":
            return "blocked by custom strategy"
        if checker is None:
            return None
        return checker(command.get("type", ""), command.get("params", {}) or {})


def test_custom_handler_resolution_strategy():
    d = Dispatcher(handler_resolution_strategy=CustomHandlerResolution())
    result = d.dispatch("synthetic_handler", {"x": 42})
    assert result == {"ok": True, "echo": 42}


def test_custom_policy_strategy_blocks():
    d = Dispatcher(policy_strategy=CustomPolicyStrategy())
    out = d.dispatch_command({"type": "blocked_command", "params": {}})
    assert out["status"] == "error"
    assert out["error_code"] == "policy_denied"
    assert "custom strategy" in out["message"]

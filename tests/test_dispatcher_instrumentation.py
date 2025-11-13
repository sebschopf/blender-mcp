from __future__ import annotations

from typing import Any

from blender_mcp.dispatchers.dispatcher import Dispatcher
from blender_mcp.dispatchers.strategies import InstrumentationStrategy
from blender_mcp.errors import InvalidParamsError


class RecordingInstrumentation(InstrumentationStrategy):
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def on_dispatch_start(self, name: str, params: dict[str, Any]) -> None:
        self.events.append(("start", {"name": name, "params": params}))

    def on_dispatch_success(self, name: str, result: Any, elapsed_s: float) -> None:
        self.events.append(("success", {"name": name, "result": result, "elapsed": elapsed_s}))

    def on_dispatch_error(self, name: str, error: Exception, elapsed_s: float) -> None:
        self.events.append(("error", {"name": name, "error": str(error), "elapsed": elapsed_s}))

    def on_adapter_invoke(self, adapter_name: str, cmd_type: str, params: dict[str, Any]) -> None:
        self.events.append(("adapter_invoke", {"adapter": adapter_name, "cmd_type": cmd_type, "params": params}))


def test_instrumentation_success():
    rec = RecordingInstrumentation()
    d = Dispatcher(instrumentation_strategy=rec)

    def echo(p: dict[str, Any]) -> dict[str, Any]:
        return {"status": "success", "result": p.get("x", 0)}

    d.register("echo", echo, overwrite=True)  # type: ignore[arg-type]
    res = d.dispatch("echo", {"x": 5})
    assert res == {"status": "success", "result": 5}

    # Check events ordering and contents
    kinds = [k for k, _ in rec.events]
    assert kinds[:2] == ["start", "success"]
    success_evt = rec.events[1][1]
    assert success_evt["result"] == {"status": "success", "result": 5}
    assert success_evt["elapsed"] >= 0.0


def test_instrumentation_error():
    rec = RecordingInstrumentation()
    d = Dispatcher(instrumentation_strategy=rec)

    def boom(_p: dict[str, Any]) -> None:
        raise InvalidParamsError("bad")

    d.register("boom", boom, overwrite=True)  # type: ignore[arg-type]
    try:
        d.dispatch("boom", {})
    except Exception:  # noqa: S110
        pass
    kinds = [k for k, _ in rec.events]
    assert kinds[:2] == ["start", "error"]
    err_evt = rec.events[1][1]
    assert "bad" in err_evt["error"]
    assert err_evt["elapsed"] >= 0.0


def test_instrumentation_adapter_invoke():
    rec = RecordingInstrumentation()
    d = Dispatcher(instrumentation_strategy=rec)

    # Minimal command adapter usage: register a handler that returns dict
    def tool(_p: dict[str, Any]) -> dict[str, Any]:
        return {"status": "success", "result": 1}

    d.register("tool", tool, overwrite=True)  # type: ignore[arg-type]
    cmd: dict[str, Any] = {"type": "tool", "params": {}}
    out = d.dispatch_command(cmd)
    assert "status" in out and out["status"] == "success"
    kinds = [k for k, _ in rec.events]
    assert "adapter_invoke" in kinds
    adapter_evt = [e for e in rec.events if e[0] == "adapter_invoke"][0][1]
    assert adapter_evt["cmd_type"] == "tool"

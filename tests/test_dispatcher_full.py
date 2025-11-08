import time

import pytest

from blender_mcp.dispatcher import Dispatcher, register_default_handlers


def test_register_duplicate_raises():
    d = Dispatcher()
    d.register("x", lambda p: 1)
    with pytest.raises(ValueError):
        d.register("x", lambda p: 2)


def test_dispatch_strict_missing_raises():
    d = Dispatcher()
    with pytest.raises(KeyError):
        d.dispatch_strict("nope")


def test_dispatch_with_timeout():
    d = Dispatcher()

    def slow(params):
        time.sleep(0.2)
        return "done"

    d.register("slow", slow, overwrite=True)
    with pytest.raises(TimeoutError):
        d.dispatch_with_timeout("slow", {}, timeout=0.05)

    # quick handler works
    d.register("quick", lambda p: "ok", overwrite=True)
    assert d.dispatch_with_timeout("quick", {}, timeout=0.1) == "ok"


def test_dispatch_command_success_and_error():
    d = Dispatcher()

    def ok_handler(params):
        return {"val": params.get("n", 0)}

    d.register("ok", ok_handler, overwrite=True)
    resp = d.dispatch_command({"type": "ok", "params": {"n": 3}})
    assert resp["status"] == "success"
    assert resp["result"] == {"val": 3}

    def explode(params):
        raise RuntimeError("boom")

    d.register("err", explode, overwrite=True)
    resp2 = d.dispatch_command({"type": "err"})
    assert resp2["status"] == "error"


def test_register_default_handlers():
    d = Dispatcher()
    register_default_handlers(d)
    assert "add_primitive" in d.list_handlers()

from __future__ import annotations

from blender_mcp.dispatchers.abc import AbstractDispatcher
from blender_mcp.dispatchers.dispatcher import Dispatcher, _CommandDispatcherCompat, register_default_handlers


def test_dispatcher_implements_abstract_dispatcher() -> None:
    d = Dispatcher()
    assert isinstance(d, AbstractDispatcher)
    # basic register/dispatch behavior remains unchanged
    d.register("foo", lambda params: "ok", overwrite=True)
    assert "foo" in d.list_handlers()
    assert d.dispatch("foo") == "ok"


def test_command_dispatcher_compat_still_works() -> None:
    c = _CommandDispatcherCompat()
    c.register("x", lambda params, config=None: {"ok": True})
    assert "x" in c.list_handlers()
    assert c.dispatch("x", {"a": 1}) == {"ok": True}


def test_register_default_handlers_no_error() -> None:
    d = Dispatcher()
    register_default_handlers(d)
    assert "add_primitive" in d.list_handlers()
    assert "create_dice" in d.list_handlers()

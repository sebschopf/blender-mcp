from blender_mcp.dispatchers.dispatcher import Dispatcher


def test_dispatcher_register_and_dispatch():
    d = Dispatcher()

    def handler(params):
        return {"ok": True, "value": params.get("v", 1)}

    d.register("add", handler)
    res = d.dispatch("add", {"v": 3})
    assert res == {"ok": True, "value": 3}

    # list_handlers and unregister behavior
    assert "add" in d.list_handlers()
    d.unregister("add")
    assert "add" not in d.list_handlers()

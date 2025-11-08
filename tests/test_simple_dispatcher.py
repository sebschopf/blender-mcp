from blender_mcp.dispatcher import Dispatcher, register_default_handlers
from blender_mcp.server import BlenderMCPServer


def test_dispatcher_register_and_dispatch():
    d = Dispatcher()
    assert d.list_handlers() == []

    d.register("t1", lambda params: {"r": params.get("x", 0)})
    assert "t1" in d.list_handlers()
    assert d.dispatch("t1", {"x": 5}) == {"r": 5}
    assert d.dispatch("missing") is None


def test_register_default_handlers_and_server_integration():
    d = Dispatcher()
    register_default_handlers(d)
    assert "add_primitive" in d.list_handlers()

    s = BlenderMCPServer()
    # ensure server uses dispatcher and default handler
    resp = s.execute_command({"tool": "add_primitive", "params": {"type": "sphere"}})
    assert resp["status"] == "ok"
    assert resp.get("handled") is True
    assert resp["result"]["primitive"] == "sphere"

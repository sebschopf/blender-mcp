from blender_mcp.dispatchers.dispatcher import Dispatcher
from blender_mcp.services import execute


def test_register_execute_handler_and_dispatch(monkeypatch):
    d = Dispatcher()

    # provide a fake bpy module so execute_blender_code can run exec(code)
    class FakeBpy:
        pass

    monkeypatch.setattr("importlib.import_module", lambda name: FakeBpy() if name == "bpy" else __import__(name))

    # register handlers
    execute.register_handlers(d)

    # dispatch via dispatch_command adapter
    cmd = {"type": "execute_blender_code", "params": {"code": "result = 42"}}
    res = d.dispatch_command(cmd)
    assert res["status"] == "success"
    # the service itself returns a status/result dict; dispatch_command
    # wraps that result as the 'result' field, so we expect a nested dict
    inner = res["result"]
    assert isinstance(inner, dict)
    assert inner.get("status") == "success"
    assert inner.get("result") == 42

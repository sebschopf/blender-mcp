from blender_mcp.server import BlenderMCPServer


def test_server_initializes_dispatcher_and_fallback_echo():
    srv = BlenderMCPServer()

    cmd = {"tool": "nonexistent_tool", "params": {"a": 1}}
    res = srv.execute_command(cmd)

    # Should return an echo fallback when no handler is registered for the tool
    assert isinstance(res, dict)
    assert res.get("echo") == cmd

    # Dispatcher should have been created lazily
    assert getattr(srv, "_dispatcher", None) is not None
    # Default handlers should be registered (at least add_primitive is expected)
    assert "add_primitive" in srv._dispatcher.list_handlers()

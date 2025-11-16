# 0001 Tasks

1. Implement `src/blender_mcp/servers/embedded_adapter.py` with `start_server_process` and `stop_server_process`.
2. Update `src/blender_mcp/blender_ui` operators to lazy-import the adapter and call the adapter functions (tests patch `blender_mcp.servers.embedded_adapter`).
3. Add unit tests `tests/test_addon_server_ui.py` that monkeypatch subprocess to avoid launching real processes.
4. Add a small README and run `openspec validate` for the change.

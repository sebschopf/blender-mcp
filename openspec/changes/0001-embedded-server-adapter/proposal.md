# Proposal: 0001 - Embedded server adapter

Summary
-------

Provide a minimal embedded-server adapter that can start/stop the MCP runtime in a controllable, testable way from the Blender UI. The adapter should be import-safe and provide an API for the UI operators to call.

What changes
------------
- Add an adapter module `src/blender_mcp/embedded_server_adapter.py` exposing `start_server_process` and `stop_server_process`.
- Ensure UI operators use lazy imports to call adapter functions.

Impact
------
- Affects `src/blender_mcp/blender_ui.py` and operator behavior; tests will need to mock subprocess interactions.

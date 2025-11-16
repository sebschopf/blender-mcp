# Proposal: 0001 - Embedded server adapter

Summary
-------

Provide a minimal embedded-server adapter that can start/stop the MCP runtime in a controllable, testable way from the Blender UI. The adapter should be import-safe and provide an API for the UI operators to call.

What changes
------------
Confirm and document that the adapter module lives at `src/blender_mcp/servers/embedded_adapter.py` exposing `start_server_process`, `stop_server_process` and `is_running`.

Ensure UI operators use lazy imports to call adapter functions. Tests and callers should patch `blender_mcp.servers.embedded_adapter` when needed.

Migration note
--------------
Historically this adapter was referenced from the top-level module `blender_mcp.embedded_server_adapter`. The implementation has since been moved into the `servers` package. Update any OpenSpec entries, docs or tests that still reference the old top-level path to use `blender_mcp.servers.embedded_adapter`.

Impact
------
Affects `src/blender_mcp/blender_ui.py` and operator behavior; tests will need to mock subprocess interactions.
Also affects documentation and OpenSpec entries that reference the legacy module path.

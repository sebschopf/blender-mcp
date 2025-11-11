# PR stub: Consolidate server implementation

Goal
----
Designate a single canonical server implementation and tidy shims/compat.

Files to change
- `src/blender_mcp/servers/*` -> consolidate into `src/blender_mcp/server.py` or re-export cleanly.
- Convert root shim `blender_mcp/server.py` into lazy delegating facade.

Tests
- `tests/test_server_entrypoint.py` added to validate facade exports.

OpenSpec
- `openspec/changes/consolidate-server/proposal.md` created as skeleton.

Acceptance
- Tests pass, no regression for consumers, documentation updated.

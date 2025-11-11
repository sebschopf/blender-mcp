# PR stub: Stabilize connection layer (reassembler, framing, network)

Goal
----
Make the connection layer more testable and robust: add unit tests for reassembly, framing and socket glue; extract clearer interfaces.

Files to change
- `src/blender_mcp/services/connection/reassembler.py` (tests added)
- `src/blender_mcp/services/connection/framing.py` (audit)
- `src/blender_mcp/services/connection/network_core.py` (integration tests)

Tests
- `tests/test_connection_reassembler.py` added in this branch.

Acceptance
- New tests pass locally
- No regressions in existing network-related tests


# Symbol: `BlenderMCPServer` (src/blender_mcp/server.py)

Location: `src/blender_mcp/server.py`

Current status:
- A minimal, import-safe server façade used by tests. It creates a `Dispatcher`, registers default handlers and exposes `execute_command`.

Proposal:
- Maintain the façade as the canonical test-friendly server surface. Record its public API and test contract. When refactoring handlers or changing the Dispatcher contract, create follow-up OpenSpec changes referencing this symbol to preserve compatibility.

Acceptance criteria:
- `execute_command` returns responses matching the current test contracts (see `tests/test_server.py`).
- The class documents expected command shapes and how errors are surfaced.

Tasks:
- Document public method signatures and create a small compatibility test that runs the existing test-suite against the refactored dispatcher.

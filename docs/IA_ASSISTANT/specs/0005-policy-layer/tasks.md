# 0005 Tasks

This file lists small, testable tasks to implement the policy layer described in `spec.md`.

Tasks (priority-ordered)

1. Create `src/blender_mcp/policy.py` skeleton exposing `load_policy` and `check`.
   - Unit tests: `tests/test_policy_basic.py` (allow/deny/obligations).

2. Wire `policy.check` into `Dispatcher.dispatch_command` and `BlenderMCPServer.execute_command` so that every incoming action is policy-checked.
   - Update `tests/test_server.py` to include a denied action scenario.

3. Implement audit logging for policy decisions: append-only JSON lines file with request_id/rule_id/decision/timestamp.
   - Unit tests: verify logs are written and contain expected fields.

4. Provide a sample policy file `openspec/changes/0005-policy-layer/sample_policy.yaml` with deny of arbitrary `system.exec` and allow of `polyhaven.search`.

5. Add CI smoke test to validate `policy.check` API and that dispatcher rejects denied actions (E2E harness will cover later).

Notes:
- Keep implementations small and pure. The policy module must not import heavy dependencies.

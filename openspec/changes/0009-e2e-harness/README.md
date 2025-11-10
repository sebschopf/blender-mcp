# 0009 - E2E harness (mock LLM) and acceptance tests

Proposal: Provide an E2E harness that simulates an LLM client sending commands through MCP to the server/dispatcher and verifies end-to-end policy, sandboxing and audit behaviour.

Why: Unit tests are insufficient to validate the full safety surface; an E2E harness will help validate integration points and regression test the safety policies.

Scope:
- A small harness (pytest-based) that spins up the server façade, injects a mock LLM client, and asserts expected outcomes.

Acceptance criteria:
- E2E tests that simulate allowed and denied commands and verify audit logs and policy outcomes.

Tasks:
1. Create E2E harness spec and directory `tests/e2e/` with at least two cases (allow/deny).
2. Wire harness to continuous integration and document how to run locally with `PYTHONPATH=src`.

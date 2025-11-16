# 0009 Tasks

1. Create `tests/e2e/` and add two baseline cases: `test_e2e_allow.py` and `test_e2e_deny.py` that use the harness.
2. Implement a small harness module `tests/e2e/harness.py` that boots `BlenderMCPServer` in-process and collects audit logs.
3. Wire E2E tests into CI as an optional smoke job (skip heavy external calls via mocks).

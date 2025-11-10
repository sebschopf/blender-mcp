# 0009 - E2E harness: spec

Scenarios
---------

1. Allowed action: mock LLM requests a benign `polyhaven.search` → server dispatches, policy allows, handler runs (mocked), audit log contains `allow` decision.
2. Denied action: mock LLM requests `system.exec` → policy denies, dispatcher returns denied response and audit log contains `deny` decision.

Harness API
-----------

- `harness.run_case(case_id: str) -> HarnessResult` where `HarnessResult` includes response, audit lines, metrics snapshot.

Acceptance
----------

- E2E tests run in CI (with mocked external services) and validate decisions and audit logs.

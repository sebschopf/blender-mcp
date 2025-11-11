## ADDED Requirements

### Requirement: E2E harness for allow/deny scenarios
The project SHALL provide an E2E harness that can simulate LLM-driven commands and assert policy decisions, handler invocation and audit log entries for representative allow and deny scenarios.

#### Scenario: E2E allow flow
- **WHEN** the harness sends a `polyhaven.search` action
- **THEN** policy allows the action, dispatcher invokes the mocked handler, and an audit log entry with `decision: allow` is emitted

#### Scenario: E2E deny flow
- **WHEN** the harness sends a `system.exec` action
- **THEN** policy denies the action and an audit log entry with `decision: deny` is emitted

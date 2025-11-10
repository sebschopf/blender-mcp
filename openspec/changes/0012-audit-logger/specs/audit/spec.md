# Audit delta spec


## ADDED Requirements

### Requirement: Audit sink append-only

The audit sink MUST be append-only and resilient to concurrent writes (test via unit test harness).

#### Scenario: Command audited

- Given a command is executed
- When the command finishes
- Then an audit JSONL line exists containing the `request_id` and result.

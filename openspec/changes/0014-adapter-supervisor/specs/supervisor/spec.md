# Supervisor delta spec


## ADDED Requirements

### Requirement: Supervisor API and backoff

The Supervisor MUST expose an API for start/stop/status and MUST support a configurable backoff policy. Tests MUST simulate failure and assert restart attempts.

#### Scenario: Restart on failure

- Given a supervised process that exits unexpectedly
- When the supervisor observes the exit
- Then the supervisor MUST attempt to restart the process according to the configured backoff policy.

## ADDED Requirements

### Requirement: Adapter sandboxing with resource limits
The embedded server adapter SHALL support running child workloads with configurable timeouts and memory limits; long-running or over-memory processes SHALL be terminated and logged.

#### Scenario: Timeout enforcement
- **WHEN** a process is started with `timeout_sec=1` and it sleeps for 5 seconds
- **THEN** the adapter terminates the process after ~1 second and records a timed-out status

### Requirement: Supervisor restart policy
The system SHALL provide a supervisor that can restart failed processes according to a configurable restart policy (never|on-failure|always) with backoff.

#### Scenario: Backoff on repeated failures
- **WHEN** a process fails repeatedly
- **THEN** the supervisor applies exponential backoff and records restart attempts

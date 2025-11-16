## ADDED Requirements

### Requirement: Audit logs with request-id
The system SHALL emit an append-only audit log entry for each incoming command including `request_id`, `timestamp`, `action`, and `decision` (if policy applied).

#### Scenario: Audit entry exists for a denied action
- **WHEN** a denied action is processed
- **THEN** an audit log line is appended containing `request_id`, `decision":"deny"`, and `reason`

### Requirement: Health and metrics endpoints
The system SHALL expose `GET /health` and `GET /metrics` providing basic service health and counters for executed/denied actions.

#### Scenario: Health endpoint returns OK
- **WHEN** the server is running and supervisor reports process counts within thresholds
- **THEN** `GET /health` returns HTTP 200

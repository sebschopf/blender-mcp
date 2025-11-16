# Policy design delta spec


## ADDED Requirements

### Requirement: Threat model includes exfiltration

The policy design MUST include a clear threat model enumerating: code execution abuse, secrets exfiltration, network exfiltration, resource exhaustion.

#### Scenario: Threat model includes exfiltration

- Given a documented threat model
- When reviewers read it
- Then it must list at least code execution abuse, secrets exfiltration, network exfiltration, and resource exhaustion.

### Requirement: Engine options documented

The design MUST propose at least two engine options (simple YAML rules and an expression engine) and discuss tradeoffs.

#### Scenario: Engine options documented

- Given the design doc
- When it is reviewed
- Then it describes at least two engine options and their tradeoffs.

### Requirement: Default fail-safe behavior

The design MUST specify default fail-safe behavior (deny by default) and test scenarios.

#### Scenario: Policy unavailable

- Given the policy service is unreachable
- When an execution request is evaluated
- Then the system denies the request and records the denial in the audit log.

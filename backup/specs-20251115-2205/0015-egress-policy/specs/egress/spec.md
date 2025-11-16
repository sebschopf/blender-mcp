# Egress delta spec


## ADDED Requirements

### Requirement: Egress checker behavior

The egress checker MUST be able to determine allow/deny for hostnames and IPs and MUST be usable by the adapter supervisor before starting a process.

#### Scenario: Deny host

- Given an allowlist that does not include `evil.example` 
- When the adapter attempts to start a process that would connect to `evil.example`
- Then the egress checker MUST return deny and the supervisor MUST prevent the process from starting.

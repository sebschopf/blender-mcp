# Secrets broker delta spec


## ADDED Requirements

### Requirement: Secrets not logged

Secrets MUST not be present in logs or audit entries; only references/IDs are allowed.

#### Scenario: Secrets not logged

- Given a secret is stored in the broker and used by a service
- When the service executes actions that reference the secret
- Then the audit entries and logs MUST NOT contain the secret plaintext (only an opaque reference/ID).

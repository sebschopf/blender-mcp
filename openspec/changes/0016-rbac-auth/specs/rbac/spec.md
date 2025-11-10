# RBAC delta spec

## ADDED Requirements

### Requirement: Role to scope mapping

The RBAC design MUST include a mapping of roles (admin/operator/viewer) to action scopes (e.g., start-server, execute-code, manage-secrets).

#### Scenario: Role mapping exists

- Given the RBAC design document
- When reviewed
- Then it contains a table mapping roles to scopes for at least the actions: start-server and execute-code.

### Requirement: Dispatcher enforcement

The system MUST provide a prototype enforcement hook in the dispatcher that checks the token's scopes before allowing a privileged action.

#### Scenario: Dispatcher denies without scope

- Given a token missing the execute-code scope
- When a request to execute code is submitted
- Then the dispatcher MUST deny the request and record the denial in the audit log.

## ADDED Requirements

### Requirement: Declarative policy check API
The system SHALL provide a policy module exposing `policy.check(action: Dict) -> PolicyDecision` that evaluates LLM actions and returns a decision object with `decision` (allow|deny|ask) and an explanatory `reason`.

#### Scenario: Deny dangerous action
- **WHEN** the dispatcher sends an action `{tool: "system", action: "exec"}`
- **THEN** `policy.check` returns a decision `deny` and `reason` explaining the denial

#### Scenario: Allow benign action
- **WHEN** the dispatcher sends `{tool: "polyhaven", action: "search"}`
- **THEN** `policy.check` returns `allow` and dispatcher proceeds to handler

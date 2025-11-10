# CI delta spec

## ADDED Requirements

### Requirement: OpenSpec validation CI job

The CI pipeline MUST include a job that runs `openspec validate --strict` against all changes in the repository and fail the PR if validation fails.

#### Scenario: OpenSpec job fails on invalid change

- Given a change with missing deltas
- When a PR is opened
- Then the CI job MUST fail and report the validation errors.

### Requirement: Optional E2E mock job

The repository MUST include an optional job definition that can run the E2E harness in mock mode; this job MAY be configured as optional in CI.

#### Scenario: E2E mock job runs

- Given the optional E2E job is enabled
- When the job runs
- Then it executes the harness in mock mode and reports pass/fail status.

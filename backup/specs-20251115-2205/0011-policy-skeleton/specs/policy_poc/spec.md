# Policy POC spec


## ADDED Requirements


### Requirement: Policy POC API and tests

The policy POC MUST provide `load_policy` and `check(action, context)` and MUST include unit tests that run under `PYTHONPATH=src` verifying that `policy.check` returns `{'allowed': True}` or `{'allowed': False, 'reason': ...}` for sample rules.

#### Scenario: Basic allow/deny

- Given a sample policy YAML fixture
- When `load_policy` loads it and `check` is called for an allowed action
- Then `check` returns `{'allowed': True}` and for a denied action returns `{'allowed': False, 'reason': '...'}.

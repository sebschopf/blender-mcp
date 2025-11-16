# Proposal: 0005 - Policy layer

Overview
--------

Introduce a declarative policy layer that evaluates LLM-suggested actions before execution. The policy layer will be minimal, data-first, and suitable for unit testing.

Goals
-----

- Provide `policy.check(action)` integration point for dispatcher and server.
- Support allow/deny/ask decisions and obligations.
- Produce auditable decisions written to the audit log.

Deliverables
------------

1. `spec.md` describing policy schema and API (already present).
2. `tasks.md` listing small testable tasks (already present).
3. A sample policy file and unit tests.

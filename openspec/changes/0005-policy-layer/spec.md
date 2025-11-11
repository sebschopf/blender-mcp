# 0005 - Policy layer: spec

Purpose
-------
This document specifies the policy layer required to validate and gate LLM-driven actions before execution by MCP. The policy layer provides:

- A declarative policy format (JSON/YAML) for allow/deny rules.
- A runtime API `policy.check(action: Dict) -> PolicyDecision` used by the dispatcher and server.
- A policy decision model describing Allow / Deny / Ask (and metadata for reasons and obligations).

Policy model
------------

PolicyDecision (JSON schema)

```json
{
  "type": "object",
  "properties": {
    "decision": {"type": "string", "enum": ["allow","deny","ask"]},
    "reason": {"type": "string"},
    "obligations": {"type": "array", "items": {"type":"string"}},
    "metadata": {"type": "object"}
  },
  "required": ["decision"]
}
```

Action shape (input to policy.check)
------------------------------------

An action is a JSON-like dict produced by the LLM translator or dispatcher. Minimal recommended shape:

```json
{
  "tool": "string",
  "action": "string",
  "params": {"type":"object"},
  "request_id": "string",
  "user": {"id":"string","roles":["string"]}
}
```

Policy language & rules
-----------------------

- Policies are expressed as a list of rules evaluated top-down. Each rule matches an action by tool/action/param patterns and returns a decision and optional obligations (e.g. redact_output=true).
- Example rule (YAML):

```yaml
- id: deny-shell
  match:
    tool: system
    action: exec
  decision: deny
  reason: "Arbitrary shell execution is forbidden"
```

Runtime API
-----------

The runtime `policy` module exposes:

- `load_policy(path: str) -> PolicySet`
- `policy.check(action: Dict) -> PolicyDecision`
- `policy.evaluate_rules(action: Dict) -> List[RuleEvaluation]` (debug mode)

Integration points
------------------

- `src/blender_mcp/dispatcher.py` must call `policy.check` before invoking handlers.
- `src/blender_mcp/server.py` should optionally short-circuit and return a structured denied response when policy denies.

Logging & audit
---------------

Each policy decision must be logged to the audit sink with: request_id, rule_id(s) matched, decision, reason, and timestamp.

Test cases / Acceptance
-----------------------

Minimum unit tests:

1. deny rule prevents execution and produces a policy decision with `decision: deny` and a clear reason.
2. allow rule permits execution and may include obligations which the dispatcher honors.
3. ask decision returns `ask` and triggers the higher-level flow (manual approval / interactive) — optional.

Security considerations
-----------------------

- Policy evaluation must run in-process and must not execute user-provided code. Rules are declarative and data-only.
- Policy files are authenticated / access-controlled in the deployment environment.

# 0005 - Policy layer: validation and action allowlists

Proposal: Introduce a central policy & safety layer that validates requested LLM actions and enforces allowlists and deny rules before any execution or side-effecting operation is performed by MCP.

Why: To satisfy security guidance (least privilege and action filtering) we must explicitly gate each action requested by an LLM and require an approval check before executing file-system, network or external process calls.

Scope:
- Add a `policy` module with an API `policy.check(action: Dict) -> PolicyDecision`.
- Integrate policy checks into `src/blender_mcp/dispatcher.py` and `src/blender_mcp/server.py`.

Acceptance criteria:
- All dispatch paths call into `policy.check` and refuse to run when policy denies.
- There is a JSON/YAML policy format and unit tests demonstrating deny/allow cases.

Tasks:
1. Add `openspec/changes/0005-policy-layer/spec.md` describing schema and examples.
2. Implement a skeletal policy module and wire into dispatcher with tests.
3. Extend openspec with per-action entries for any previously-unchecked dangerous operations.

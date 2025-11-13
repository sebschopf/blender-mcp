# Spec: Security Policy for `execute_blender_code`

Status: proposed
Date: 2025-11-13
Author: automation
Scope: `services/execute.py::execute_blender_code`
Phase: 2 (baseline), Phase 3 (tightening)

## Summary
Define a minimal, explicit security policy for the `execute_blender_code` service. Phase 2 delivers a baseline with audit logging and explicit limitations; Phase 3 will introduce a restricted execution environment (sandbox) or AST allowlist to enforce constraints.

## Motivation
Executing arbitrary code in Blender is powerful but risky. We need a documented policy and acceptance scenarios so adapters and UIs can communicate limits and so future hardening (Phase 3) doesn’t break clients unexpectedly.

## Non-Goals
- Implementing a full sandbox in this change. This spec documents policy; the stricter enforcement will land in a subsequent change.
- Changing external APIs beyond what’s already used in tests.

## Policy (Phase 2 Baseline)
- Environment: code is executed only when Blender (`bpy`) is importable. If not, raise `ExternalServiceError("Blender (bpy) not available")`.
- Namespace: globals passed to `exec` expose `bpy` only; results should be written to a variable named `result` that will be returned to the caller.
- Builtins: Python builtins remain available in Phase 2 (limitation). This is explicitly documented and will be addressed in Phase 3.
- Disallowed intents (policy): filesystem writes, subprocess spawning, network access, or long-running loops. Phase 2 does not enforce programmatically; UIs must warn users and keep snippets small; server logs all attempts.
- Audit: an audit logger records code length and outcome (`blender_mcp_execute.log`). Env `BLENDER_MCP_EXECUTE_DRY_RUN=1` skips execution and returns a message.
- Errors: wrap runtime exceptions in `HandlerError("execute_blender_code", original)`.
- Contract: on success, return `{"status":"success","result": <any>}`; on failure, raise canonical exceptions (not error dicts).

## Phase 3 (Planned Tightening)
- Restricted execution: remove default builtins or provide a curated `__builtins__` (e.g., read-only subset) and/or enforce an AST allowlist.
- Deny imports: block `import` statements except a curated allowlist (none by default).
- Time/memory guard: optional micro timeouts at statement level or external watchdog to abort long-running code.
- Config: allow an adapter/server-level policy to disable the endpoint entirely.

## API Contract
- Input: `params: { code: str }` (required)
- Output (success): `{"status":"success","result": any}` where `result` is the value set in the snippet.
- Exceptions: `InvalidParamsError` (missing/invalid code), `ExternalServiceError` (no bpy), `HandlerError` (runtime error in code).

## Acceptance Scenarios

#### Scenario: Missing code parameter
Given params `{}`
When calling `execute_blender_code`
Then it raises `InvalidParamsError`.

#### Scenario: Blender not available
Given `bpy` is not importable
When calling `execute_blender_code` with any code
Then it raises `ExternalServiceError("Blender (bpy) not available")`.

#### Scenario: Success returns result
Given `bpy` is importable
And code `result = 'ok'`
When calling `execute_blender_code`
Then it returns `{ "status": "success", "result": "ok" }`.

#### Scenario: Runtime error is wrapped
Given `bpy` is importable
And code `raise ValueError('boom')`
When calling `execute_blender_code`
Then it raises `HandlerError` with original message containing `boom`.

#### Scenario: Dry-run skips execution
Given env `BLENDER_MCP_EXECUTE_DRY_RUN=1`
And valid code
When calling `execute_blender_code`
Then it returns a message indicating dry-run (status ok) and does not execute the code.

## Compatibility
The Phase 2 baseline matches current tests and behavior. Future Phase 3 tightening will be introduced behind a feature flag or minor version bump with migration notes.

## Rollout & Validation
- Land spec (this change), keep current implementation as-is.
- Add a follow-up change to introduce optional restricted execution (guarded by an env/config switch), with additional unit tests.
- Adapters/UI: show a warning banner for execute, linking to this policy.

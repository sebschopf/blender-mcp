# spec — 0012-audit-logger (new)

ADDED:
- Requirement: Audit events MUST be persisted as JSONL lines with at least: timestamp, request_id, actor, action, result.
- Requirement: `server.execute_command` must generate a `request_id` per invocation and ensure it appears in the audit entry.

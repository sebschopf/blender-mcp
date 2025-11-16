# 0008 - Observability, audit logs and metrics

Proposal: Add structured audit logging, request identifiers, and Prometheus-style metrics to MCP. Also expose `/health` and `/metrics` endpoints from `server.py`.

Why: Required for security investigations, monitoring and to satisfy the auditability requirements discussed in the MCP article.

Scope:
- Add request-id generation and append-only audit logs for execution requests.
- Add `server.py` endpoints for health and metrics; wire an in-process Prometheus collector or a simple counters shim.

Acceptance criteria:
- Each incoming command is logged with request-id, timestamp, user (if available), and action metadata.
- Health and metrics endpoints respond and are covered by smoke tests.

Tasks:
1. Add spec and example logs for the audit format.
2. Implement `/health` and `/metrics` in `server.py` and add tests.

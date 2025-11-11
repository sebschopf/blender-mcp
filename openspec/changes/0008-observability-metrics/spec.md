# 0008 - Observability & Metrics: spec

Log format
----------

Audit log entries are JSON-lines with these fields:

```json
{
 "timestamp":"ISO8601",
 "request_id":"string",
 "user":"string|null",
 "action":"string",
 "decision":"allow|deny|ask|null",
 "details":{ }
}
```

Endpoints
---------

- `GET /health` returns 200 when service is up and supervisor/process counts are within thresholds.
- `GET /metrics` returns Prometheus-format counters: `mcp_executions_total`, `mcp_policy_denied_total`, `mcp_process_running`.

Acceptance
----------

1. Each executed request emits an audit log line with a request_id.
2. Health and metrics endpoints respond and are covered by tests.

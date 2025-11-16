# 0007 - Secrets broker: spec

Specification
-------------

The secrets broker provides a narrow RPC interface used by services that need to perform privileged API calls without exposing secrets to untrusted runtimes.

Broker API (example)
--------------------

POST /broker/call

Request:

```json
{
  "service": "sketchfab",
  "operation": "download_metadata",
  "params": {"uid":"abc123"},
  "request_id": "..."
}
```

Response:

```json
{
  "status":"ok",
  "result": { ... }
}
```

Rules
-----

- The broker never returns raw secrets in responses.
- The broker authenticates callers and logs every request to the audit sink.

Acceptance tests
----------------

1. Broker returns expected data for allowed service/operation.
2. Broker refuses unknown operations and logs the attempt.

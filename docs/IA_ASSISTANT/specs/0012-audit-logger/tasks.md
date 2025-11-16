# Tasks — 0012 Audit logger

1. Implementer `src/blender_mcp/audit.py` avec fonction `log_event(event_dict)` et `generate_request_id()`.
2. Wire `server.execute_command` to generate and return `request_id` and call `log_event` on start/end/failure.
3. Tests: `tests/test_audit_logger.py` qui vérifient écriture JSONL et propagation du `request_id`.

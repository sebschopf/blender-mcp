# 0008 Tasks

1. Implement small audit logger helper under `src/blender_mcp/audit.py` that appends JSON-lines to a configured logfile.
2. Add `request_id` generation to `server.execute_command` and include it in all logs.
3. Add `/health` and `/metrics` endpoints in `src/blender_mcp/server.py` (lightweight; no external deps) and tests under `tests/test_metrics.py`.
4. Add CI smoke test that checks `/health` responds 200.

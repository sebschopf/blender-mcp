# 0007 Tasks

1. Draft broker API (HTTP/Local RPC) and implement a simple in-process proof-of-concept under `src/blender_mcp/secrets_broker.py`.
2. Port one service (e.g., Sketchfab) to call the broker instead of using raw API keys, add unit tests demonstrating the flow.
3. Add audit logging and tests verifying the broker never returns raw secrets.

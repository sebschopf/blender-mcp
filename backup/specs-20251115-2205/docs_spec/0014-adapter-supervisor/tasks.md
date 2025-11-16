# Tasks — 0014 Adapter supervisor

1. Implement a light POC `src/blender_mcp/adapter_supervisor.py` supporting start/stop/restart with exponential backoff.
2. Add unit tests simulating child exit and verifying restart behavior.
3. Document configuration surface (max_restarts, backoff_base) in README.

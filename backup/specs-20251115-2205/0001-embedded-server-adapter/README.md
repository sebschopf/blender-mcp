Title: Embedded server adapter (out-of-process)

Summary
-------
Provide an optional, small adapter to run the historical embedded server in a
separate process instead of in-process inside Blender. This reduces risk of
threading and lifecycle issues and keeps the addon import-safe.

Motivation
----------
- Historical behavior: the addon started an in-process socket server. That
  caused import-time side-effects and threading difficulties inside Blender.
- New approach: keep the addon lightweight and provide a maintained adapter
  that can spawn an external process. The adapter is optional and intended
  for advanced users or development workflows.

Implementation
--------------
- Canonical module: `src/blender_mcp/servers/embedded_adapter.py` exposing the API: `start_server_process(command, cwd)`, `stop_server_process(proc)`, and `is_running(proc)`.
- The adapter is intentionally minimal and only spawns an external helper process supplied by callers (the adapter does not embed the runtime itself). Tests and callers should patch `blender_mcp.servers.embedded_adapter` to avoid launching real subprocesses in CI.
- On Windows a convenient default uses the repo script `scripts/start-server.ps1`.
- Tests: `tests/test_embedded_adapter.py` should mock process startup so CI does not launch real processes.

Compatibility & Migration
-------------------------
- No breaking changes to existing public APIs. The addon no longer attempts
  to start servers in-process by default.
- Developers who relied on in-process behavior should update their workflow to
  call the adapter with an appropriate command or run the server externally.

Acceptance criteria
-------------------
- The adapter module exists at `src/blender_mcp/servers/embedded_adapter.py` and exports `start_server_process`, `stop_server_process`, and `is_running`.
- UI operators perform lazy imports of `blender_mcp.servers.embedded_adapter` and tests mock the adapter to avoid launching processes in CI.
- Documentation and OpenSpec entries referencing the legacy top-level module path (`blender_mcp.embedded_server_adapter`) are updated to reference the `servers` package.

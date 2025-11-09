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
- New module: `src/blender_mcp/embedded_server_adapter.py` exposing a tiny API:
  `start_server_process(command, cwd)`, `stop_server_process(proc)`,
  `is_running(proc)`.
- The adapter does not embed a server runtime itself; callers provide the
  command to run. On Windows a convenient default uses the repo script
  `scripts/start-server.ps1`.
- Tests added to `tests/test_embedded_adapter.py` that mock process startup so
  CI does not launch real processes.

Compatibility & Migration
-------------------------
- No breaking changes to existing public APIs. The addon no longer attempts
  to start servers in-process by default.
- Developers who relied on in-process behavior should update their workflow to
  call the adapter with an appropriate command or run the server externally.

Acceptance criteria
-------------------
- New adapter module present in the `src` tree.
- Tests exercising adapter behavior run green locally and in CI.
- Documentation note and PR description included.

Summary of changes: Embedded server adapter + connection consolidation notes

What I changed
- Added `src/blender_mcp/servers/embedded_server_adapter.py`: a small adapter to
  start/stop an external server process. Defaults to the repo PowerShell
  helper on Windows when no command is provided.
- Updated `src/blender_mcp/services/connection/network.py` to prefer the
  canonical `connection_core.BlenderConnection` when available. This reduces
  duplication and ensures a single runtime implementation of the connection
  protocol.
- Added tests: `tests/test_embedded_adapter.py` exercising the adapter via
  monkeypatched subprocess calls.
- Added OpenSpec change proposal under
  `openspec/changes/0001-embedded-server-adapter/README.md` describing the
  rationale and migration steps.

Why
- The addon should remain import-safe and not create server threads/processes
  implicitly. Running the server out-of-process is safer and easier to debug.

Notes for reviewers
- The adapter intentionally does not start a server binary by itself; callers
  must provide the command to run. On Windows the repo script is used as a
  convenient default.
- Tests mock `subprocess.Popen` so CI will not launch processes.

How to test locally
1. Run unit tests: set `PYTHONPATH=src` and run `python -m pytest -q`.
2. To manually try the adapter on Windows: in a PowerShell session run the
   repository's `scripts/start-server.ps1` (or let the adapter call it when
   used from the addon UI).

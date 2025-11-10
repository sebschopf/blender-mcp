Embedded Server Adapter — Usage Guide

This short guide explains the new optional embedded-server adapter. The
adapter is intentionally minimal: it launches an external process that runs
the MCP server instead of starting server threads inside Blender. This keeps
the add-on import-safe and avoids lifecycle issues.

Quick summary
-------------
- Module: `blender_mcp.embedded_server_adapter`
- API:
  - `start_server_process(command: Optional[Iterable[str]] = None, cwd: Optional[str] = None) -> Popen`
  - `stop_server_process(proc: Popen, timeout: float = 5.0) -> None`
  - `is_running(proc: Popen) -> bool`

Defaults and recommended usage
------------------------------
- On Windows, if `command` is not provided, the adapter will use the
  repository helper `scripts/start-server.ps1` via `pwsh`.
- On non-Windows platforms you should pass an explicit command. Example:

    from blender_mcp import embedded_server_adapter as adapter
    proc = adapter.start_server_process(command=['python', '-m', 'blender_mcp.server'])
    # keep `proc` so you can stop it later
    adapter.stop_server_process(proc)

How it integrates with the add-on UI
-----------------------------------
- The addon UI provides Start/Stop operators which lazily import the
  adapter and attempt to start/stop the external server. The UI stores the
  process PID in `Scene.blendermcp_server_pid` for visibility.
- By default the UI will call the adapter and present an error message if
  starting/stopping fails. This is opt-in behavior: users can also run the
  server manually from a terminal or via the provided PowerShell helper.

Testing
-------
- Unit tests in `tests/test_embedded_adapter.py` and
  `tests/test_addon_server_ui.py` mock process creation so CI does not
  actually spawn external processes. Run the tests with `PYTHONPATH=src`.

Notes for developers
--------------------
- The adapter does not implement the server. It only provides a safe,
  documented way to run an external MCP server process from the add-on UI.
- If you need a long-running production server, prefer running it as a
  system service or as a separate process managed by your deployment tool.

If you'd like, I can add a small demo script `scripts/run_embedded_dummy.py`
that prints logs and sleeps to make local testing of the adapter trivial.

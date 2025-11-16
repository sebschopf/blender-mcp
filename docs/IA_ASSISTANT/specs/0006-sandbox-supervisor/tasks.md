# 0006 Tasks

Small actionable tasks to implement the sandboxing and supervisor features.

1. Implement `src/blender_mcp/servers/embedded_server_adapter.py` extensions:
   - Add optional parameters for `timeout_sec`, `mem_limit_mb`, `net_policy`, and `workdir`.
   - Ensure adapter spawns processes with timeouts and cleans up workdir after exit.
   - Unit tests: simulate child processes via monkeypatch and verify timeouts/cleanup.

2. Provide a simple unprivileged-process mode for Windows and Linux:
   - On Linux: use `subprocess` with `preexec_fn` setting uid/gid (when available) and `resource.setrlimit` for memory/CPU.
   - On Windows: document best-effort behavior and rely on process job objects if available.

3. Implement a supervisor module `src/blender_mcp/adapter_supervisor.py` that tracks processes and implements restart/backoff policies.

4. Add network policy enforcement option:
   - Default: deny all egress.
   - Integrations may register required host allow-lists.
   - Implementation: recommend using a local proxy (for now) and document steps to enable container network rules later.

5. Add acceptance tests in `tests/test_adapter_sandbox.py` and CI smoke checks.

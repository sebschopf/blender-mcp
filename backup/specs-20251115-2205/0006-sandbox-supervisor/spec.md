# 0006 - Sandboxing & supervisor: spec

Purpose
-------

This specification describes the sandboxing and supervisor requirements for `blender_mcp.servers.embedded_adapter` and any external workloads launched by MCP.

Goals
-----

- Execute untrusted or semi-trusted workloads in isolated environments.
- Enforce resource limits (time, CPU, memory, disk) and network egress policies.
- Provide a supervisor that can restart, back off, and report status.

Adapter API (high-level)
------------------------

The adapter exposes a defined API used by the UI and server code:

-- `start_server_process(cmd: List[str], *, timeout_sec: int, mem_limit_mb: int, net_policy: str, workdir: str) -> ProcessHandle`
-- `stop_server_process(handle: ProcessHandle) -> None`
-- `get_process_status(handle: ProcessHandle) -> ProcessStatus`

ProcessHandle and ProcessStatus
-------------------------------

ProcessHandle is an opaque object with a stable identifier. ProcessStatus includes `pid`, `state` (`running`/`exited`/`failed`), `exit_code`, `start_time`.

Sandboxing modes
-----------------

Implementations should support one of the following (platform-dependent):

1. Container mode — prefer lightweight container runtime (Docker/Podman) with explicit resource constraints and network controls.
2. Unprivileged process mode — spawn processes under a dedicated unprivileged user, use OS job objects/cgroups (Linux), and set ulimit/timeouts.

Configuration
-------------

Adapter configuration is provided via a small config object or file with defaults:

```yaml
sandbox:
  mode: container|unprivileged
  default_timeout_sec: 30
  default_mem_mb: 256
  network_default: deny
  allowed_hosts: ["polyhaven.org","api.sketchfab.com"]
  workdir_base: /tmp/mcp-runs
supervisor:
  restart_policy: never|on-failure|always
  backoff_seconds: 5
```

Health & metrics
----------------

Supervisor must expose aggregated status (number of running processes, failed restarts) for `/health` and `/metrics`.

Acceptance tests
----------------

1. Running a short-lived process returns `running` and then `exited` with expected exit code.
2. Long-running processes are killed after `timeout_sec` and logged as timed-out.
3. Memory-bound processes are killed if they exceed `mem_limit_mb`.
4. Network requests from disallowed hosts are blocked by network policy (via proxy or container network rules).

Security notes
--------------

- The adapter must never run user-supplied code as root. If container runtimes are used, avoid mounting host sensitive paths. Use ephemeral volumes.
- Log process metadata but avoid including execution stdout/stderr into audit logs unless sanitized.

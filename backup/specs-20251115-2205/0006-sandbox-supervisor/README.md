# 0006 - Sandboxing and adapter supervisor

Proposal: Harden `blender_mcp.servers.embedded_adapter` by running external workloads in isolated, resource-limited environments and add a supervisor that enforces restart policies and resource limits.

Why: Arbitrary code/workloads executed as part of MCP must be isolated with CPU/time/memory limits and have a supervisor to recover from crashes safely.

Scope:
- Provide platform-aware sandboxing (container or unprivileged process + cgroups where available).
- Add supervisor loop with configurable restart/backoff policies.

Acceptance criteria:
- Adapter supports running in a sandboxed child and enforces timeouts, memory limits and cleans up artifacts.
- Supervisor implements restart/backoff and exposes status via server health endpoints.

Tasks:
1. Spec the adapter sandbox API and config options.
2. Implement non-invasive platform-aware timeouts in the adapter and tests.
3. Implement supervisor skeleton and wire to health/metrics.

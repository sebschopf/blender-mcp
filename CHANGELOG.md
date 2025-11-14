# Changelog

## Unreleased

  - `pyproject.toml`: add `src/blender_mcp/archive/**` to `tool.ruff.exclude`
  - `mypy.ini`: add `exclude = src/blender_mcp/archive/.*`

  - `src/blender_mcp/simple_dispatcher.py` → use `blender_mcp.dispatchers`
  - `src/blender_mcp/command_dispatcher.py` → use `blender_mcp.dispatchers.command_dispatcher`
  - `src/blender_mcp/server_shim.py` → use `blender_mcp.servers.shim`
  - `src/blender_mcp/server.py` façade → use `blender_mcp.servers.server`
  - `src/blender_mcp/connection_core.py` → use `services/connection/network_core.py` and `connection.py`
  - `blender_mcp/server.py` (repo root shim) → temporary, slated for removal
  - `src/blender_mcp/polyhaven.py` → use `blender_mcp.services.polyhaven`
  - `src/blender_mcp/sketchfab.py` → use `blender_mcp.services.sketchfab`
  - `src/blender_mcp/hyper3d.py` → use `blender_mcp.services.hyper3d`
  - instrumentation: Add optional `InstrumentationStrategy` to `Dispatcher` (non-breaking extension point for logging/metrics)
  - security: Baseline safeguards for `execute_blender_code` (audit logger, dry-run env `BLENDER_MCP_EXECUTE_DRY_RUN`, minimal namespace)

Rationale: the in-repo `src/blender_mcp/archive` and `docs/archive` directories contain legacy or partial snapshots that are intentionally kept for historical/reference purposes and are not valid Python packages for static analysis nor linting. Ignoring them avoids false-positive errors in automated checks.

Notes:
- The repository still contains a repo-root shim `blender_mcp/server.py` used by a legacy test (`tests/test_blender_connection.py`). This shim was intentionally kept to preserve test behavior. Recommended follow-up: update tests to import the canonical implementation under `src/blender_mcp/connection_core.py` and remove the shim in a follow-up PR.

### Deprecation & Planned Removals (Cycle N: 2025-11)

The following legacy shims/facades are officially deprecated. They emit `DeprecationWarning` on import and are scheduled for removal no earlier than cycle N+2 (see OpenSpec `openspec/changes/2025-11-14-legacy-retirement-schedule/spec.md`).

| Component | Replacement | Planned Removal (Earliest) | Notes |
|-----------|-------------|----------------------------|-------|
| `connection_core.py` | `services/connection/network_core.py` + transport abstraction | Cycle N+2 | Retained until transport fully stabilized & external migration complete. |
| `simple_dispatcher.py` / `command_dispatcher.py` | `dispatchers/` package | Cycle N+2 | Pure re-exports; low risk removal first. |
| Root services (`polyhaven.py`, `sketchfab.py`, `hyper3d.py`) | `services/*.py` canonical implementations | Cycle N+2 | All endpoints ported exceptions-first. |
| `materials.py` | `materials/` package | Cycle N+2 | Facade only; remove after warning window. |
| `blender_codegen.py` | `codegen/blender_codegen.py` | Cycle N+2 | Transitional import path. |
| Root server shim `blender_mcp/server.py` | `servers/server.py` (or service facade) | Cycle N+2 | Double shim; consolidate before removal. |

Migration Guidance:
- New code should import only canonical modules listed under Replacement.
- For external consumers, begin updating imports now; shims will be removed after the grace period.

Operational Next Steps:
1. Create GitHub issues per component (templates in `docs/ISSUES_LEGACY_DRAFTS.md`).
2. Update `docs/LEGACY_WITHDRAWAL_PLAN.md` table with issue numbers.
3. Start removal PR sequence following recommended order (dispatcher shims first). Micro-PR constraint: ≤3 code files changed (excluding docs/tests).

Risk Mitigation:
- Two-cycle notice ensures downstream integrators have adequate migration time.
- CI parity script (`scripts/verify_local_ci.ps1`) must pass before and after each removal.


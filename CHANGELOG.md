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

  - fix: supprimer marqueurs de merge résiduels dans `src/blender_mcp/dispatchers/dispatcher.py` et corriger l'import de test (ruff) — débloque CI (PR #40)

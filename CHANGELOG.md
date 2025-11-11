# Changelog

## Unreleased

- tooling: Ignore archive snapshots in linters and mypy
  - `pyproject.toml`: add `src/blender_mcp/archive/**` to `tool.ruff.exclude`
  - `mypy.ini`: add `exclude = src/blender_mcp/archive/.*`

Rationale: the in-repo `src/blender_mcp/archive` and `docs/archive` directories contain legacy or partial snapshots that are intentionally kept for historical/reference purposes and are not valid Python packages for static analysis nor linting. Ignoring them avoids false-positive errors in automated checks.

Notes:
- The repository still contains a repo-root shim `blender_mcp/server.py` used by a legacy test (`tests/test_blender_connection.py`). This shim was intentionally kept to preserve test behavior. Recommended follow-up: update tests to import the canonical implementation under `src/blender_mcp/connection_core.py` and remove the shim in a follow-up PR.

# PR stub: Unify Dispatcher implementations

Goal
----
Unify dispatcher implementations so there is a single canonical implementation under `src/blender_mcp/dispatchers/dispatcher.py`. Keep compatibility wrappers where needed.

Files to change
- Consolidate logic from `src/blender_mcp/simple_dispatcher.py` and `src/blender_mcp/command_dispatcher.py` into `src/blender_mcp/dispatchers/dispatcher.py`.
- Add compatibility thin wrappers in `src/blender_mcp/dispatchers/compat.py` if required.

Tests added in this branch
- `tests/test_dispatcher_unify.py` — ensures basic register/dispatch semantics.

Acceptance criteria
- Tests pass locally (`pytest -q tests/test_dispatcher_unify.py`)
- `ruff` and `mypy` unchanged / pass
- No behavioral regressions for modules using old dispatcher APIs (compat wrappers in place)

Notes
- This PR is low-risk for public API, but ensure exports and alias names (e.g., `CommandDispatcher`) are preserved via adapters.

---

Local CI status (executed locally on branch `feat/unify-dispatcher`)

- pytest: full test suite executed; new tests passed locally (`tests/test_dispatcher_unify.py`, `tests/test_simple_dispatcher_compat.py`).
- ruff: All checks passed!
- mypy: Success: no issues found in 2 source files

Checklist for reviewers

- [ ] Verify tests in CI (GitHub Actions) pass on PR
- [ ] Confirm `CommandDispatcher` compatibility is preserved for existing imports
- [ ] Confirm top-level `simple_dispatcher` imports remain functional
- [ ] Merge after approval and small changelog note

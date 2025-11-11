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

# Symbol: `_lazy_attr(module: str, name: str)` (addon.py)

Location: `addon.py` (archive)

Current status:
- Helper that performs a lazy import and returns an attribute or None on failure. Used by `register`/`unregister` to avoid importing Blender UI at module import.

Proposal:
- Keep this helper in `addon.py` (import-safe shim) and add a unit-test that verifies its failure-safe behavior. If we later centralize lazy import helpers, create a port task referencing this spec.

Acceptance criteria:
- Unit tests cover success and failure paths.
- `addon.register()` and `addon.unregister()` rely on `_lazy_attr` and do not import `bpy` at top-level.

Tasks:
- Add test `tests/test_addon_lazy_imports.py` referencing this change id.

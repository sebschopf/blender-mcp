# Symbol: `bl_info` (addon.py)

Location: `addon.py` (archive)

Current status:
- Static metadata dict used by Blender add-on loader. Not behaviorally sensitive.

Proposal:
- Keep `bl_info` in `addon.py` to satisfy Blender loader. No port needed.

Acceptance criteria:
- `addon.py` continues to export `bl_info` unchanged.
- Tests that import `addon.py` in headless environment still succeed.

Tasks:
- none (document-only)

# Symbol: `register()` (addon.py)

Location: `addon.py` (archive)

Current status:
- Delegates registration to `blender_mcp.blender_ui.register` via `_lazy_attr` to remain import-safe.

Proposal:
- Keep top-level `register()` as the public add-on registration entrypoint. Create an OpenSpec task to ensure `blender_mcp.blender_ui.register` implements the actual registration logic. If porting is needed, create follow-up change to update call site.

Acceptance criteria:
- Calling `python addon.py` (or Blender registration) will not import `bpy` at module import time.
- Register delegates correctly when the UI module is present.

Tasks:
- Add a small integration test that calls `addon.register()` with `blender_mcp.blender_ui.register` monkeypatched and validates the call.

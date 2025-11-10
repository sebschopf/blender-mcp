# Symbol: `unregister()` (addon.py)

Location: `addon.py` (archive)

Current status:
- Delegates unregistration to `blender_mcp.blender_ui.unregister` via `_lazy_attr`.

Proposal:
- Keep the delegate pattern. Add tests and document migration steps if the real `unregister` is moved.

Acceptance criteria:
- `addon.unregister()` remains import-safe and delegates when UI is present.

Tasks:
- Add unit test that ensures `unregister()` calls into the UI unregister when present.

# 0002 Tasks

1. Add `AddonPreferences` implementation in `src/blender_mcp/blender_ui.py` exposing `allow_ui_start_server` with a default of `False`.
2. Update Start/Stop operators to check this preference before starting the adapter.
3. Add unit tests `tests/test_addon_preferences.py` and `tests/test_addon_server_ui.py` to validate behavior.

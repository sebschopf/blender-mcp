# Proposal: 0002 - Addon preferences

Summary
-------

Introduce an AddonPreferences entry that allows users to control whether the Blender UI can start/stop the embedded MCP server automatically. This preference preserves import-safety while allowing admins to opt-in to automatic server control.

What changes
------------
- Add an `AddonPreferences` class exposing `allow_ui_start_server: BoolProperty` and wire the Start/Stop operators to respect this setting.

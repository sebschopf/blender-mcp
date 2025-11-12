# Archive → Implementation mapping

This document maps the legacy archive symbols described in `docs/archive/symbole_addon.md` and `docs/archive/symbole_server.md` to the current implementation in `src/blender_mcp`.

Notes:
- Many legacy functions were split into smaller modules (`services/*`, `sketchfab.py`, `polyhaven.py`, `hyper3d.py`, `server.py`, `server_shim.py`).
- Where a private helper was renamed, I noted the new location and the approximate equivalent name.

## Addon symbols
- BlenderMCPServer
  - Present as `src/blender_mcp/server.py::BlenderMCPServer` and a lightweight shim `src/blender_mcp/server_shim.py`.
- execute_command / execute_wrapper / _execute_command_internal
  - Implemented in `src/blender_mcp/server.py` and wrapped by `server_shim.py`.

- get_scene_info
  - Service-facing: `src/blender_mcp/services/scene.py::get_scene_info`
  - Addon-backed: `src/blender_mcp/services/addon/scene.py::get_scene_info`

- _get_aabb
  - `src/blender_mcp/services/addon/scene.py::_get_aabb`

- get_object_info
  - Service-facing: `src/blender_mcp/services/object.py::get_object_info`
  - Addon-backed: `src/blender_mcp/services/addon/objects.py::get_object_info`

- get_viewport_screenshot
  - Service-facing: `src/blender_mcp/services/screenshots.py::get_viewport_screenshot`
  - Addon-backed: `src/blender_mcp/services/addon/screenshots.py::get_viewport_screenshot`

- execute_code
  - `src/blender_mcp/services/addon/execution.py::execute_code`

- get_polyhaven_categories / search_polyhaven_assets / download_polyhaven_asset
  - Addon implementations: `src/blender_mcp/services/addon/polyhaven.py`
  - Service wrappers and registry: `src/blender_mcp/services/registry.py` and `src/blender_mcp/integrations.py`

- set_texture
  - Service wrapper: `src/blender_mcp/services/textures.py::set_texture`
  - Addon implementation: `src/blender_mcp/services/addon/textures.py::set_texture`

- get_sketchfab_status / search_sketchfab_models / download_sketchfab_model
  - Helpers: `src/blender_mcp/sketchfab.py`
  - Service wrappers: `src/blender_mcp/services/sketchfab.py` and registration in `services/registry.py`

- Hyper3D / Rodin: create_rodin_job*, poll_rodin_job_status*, import_generated_asset*
  - Implemented in `src/blender_mcp/hyper3d.py` (main_site and fal_ai variants exist)

## Server / connection symbols
- BlenderConnection / connect / disconnect / send_command / receive_full_response
  This file has been archived and moved to `docs/archive/archive_symbol_mapping.md`.

  See `docs/archive/archive_symbol_mapping.md` for the preserved content.
  - Service-side adapters and facade:

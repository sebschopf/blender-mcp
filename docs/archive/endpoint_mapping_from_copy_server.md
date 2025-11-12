# Endpoint mapping extracted from `copy_server.py`

This file was generated automatically by `tools/parse_decorators.py`.
It lists the `@mcp.tool()` and `@mcp.prompt()` decorated functions found in `copy_server.py`, with their signatures, definition line numbers and a one-line docstring summary (when present).

| Decorator | Function Name | Signature | Def line | Docstring summary |
|---|---|---|---:|---|
| @mcp.tool() | get_scene_info | ctx: Context | 245 | Get detailed information about the current Blender scene |
| @mcp.tool() | get_object_info | ctx: Context, object_name: str | 258 | Get detailed information about a specific object in the Blender scene. |
| @mcp.tool() | get_viewport_screenshot | ctx: Context, max_size: int = 800 | 276 | Capture a screenshot of the current Blender 3D viewport. |
| @mcp.tool() | execute_blender_code | ctx: Context, code: str | 319 | Execute arbitrary Python code in Blender. Make sure to do it step-by-step by breaking it into smaller chunks. |
| @mcp.tool() | get_polyhaven_categories | ctx: Context, asset_type: str = "hdris" | 336 | Get a list of categories for a specific asset type on Polyhaven. |
| @mcp.tool() | search_polyhaven_assets | ctx: Context, asset_type: str = "all", categories: str = None | 368 |  |
| @mcp.tool() | download_polyhaven_asset | ctx: Context, asset_id: str, asset_type: str, resolution: str = "1k", file_format: str = None | 417 |  |
| @mcp.tool() | set_texture | ctx: Context, object_name: str, texture_id: str | 468 |  |
| @mcp.tool() | get_polyhaven_status | ctx: Context | 527 | Check if PolyHaven integration is enabled in Blender. |
| @mcp.tool() | get_hyper3d_status | ctx: Context | 545 | Check if Hyper3D Rodin integration is enabled in Blender. |
| @mcp.tool() | get_sketchfab_status | ctx: Context | 565 | Check if Sketchfab integration is enabled in Blender. |
| @mcp.tool() | search_sketchfab_models | ctx: Context, query: str, categories: str = None, count: int = 20, downloadable: bool = True | 583 |  |
| @mcp.tool() | download_sketchfab_model | ctx: Context, uid: str | 660 |  |
| @mcp.tool() | generate_hyper3d_model_via_text | ctx: Context, text_prompt: str, bbox_condition: list[float]=None | 712 |  |
| @mcp.tool() | generate_hyper3d_model_via_images | ctx: Context, input_image_paths: list[str]=None, input_image_urls: list[str]=None, bbox_condition: list[float]=None | 748 |  |
| @mcp.tool() | poll_rodin_job_status | ctx: Context, subscription_key: str=None, request_id: str=None | 804 |  |
| @mcp.tool() | import_generated_asset | ctx: Context, name: str, task_uuid: str=None, request_id: str=None | 847 |  |
| @mcp.prompt() | asset_creation_strategy |  | 880 | Defines the preferred strategy for creating assets in Blender |

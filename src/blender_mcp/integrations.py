import base64
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union, cast
from urllib.parse import urlparse

from mcp.server.fastmcp import Context

from .tools import get_blender_connection, mcp

# Local logger (avoid importing server at module-import time)
logger = logging.getLogger(__name__)

# Feature flag fallback; server may provide a different value at runtime.
_polyhaven_enabled = True
from .services import sketchfab as services_sketchfab
from .services.hyper3d import prepare_rodin_payload
from .services.polyhaven import (
    download_asset,
    fetch_categories,
    format_categories_output,
    format_search_assets,
    search_assets_network,
)


def _process_bbox(
    original_bbox: Optional[Sequence[float]] = None,
) -> Optional[List[int]]:
    """Normalize a bbox (sequence of numbers) into percentages as ints or return None."""
    if original_bbox is None:
        return None
    try:
        vals = [float(i) for i in original_bbox]
    except Exception:
        raise ValueError("bbox must be a sequence of numbers")
    if any(i <= 0 for i in vals):
        raise ValueError("Incorrect number range: bbox must be bigger than zero!")
    m = max(vals)
    if m == 0:
        raise ValueError("Max bbox dimension is zero")
    return [int(i / m * 100) for i in vals]


@mcp.tool()
def get_polyhaven_categories(
    ctx: Context[Any, Any, Any], asset_type: str = "hdris"
) -> str:
    """
    Get a list of categories for a specific asset type on Polyhaven
    """
    try:
        # Prefer server-side fetch; fallback to asking Blender addon when needed
        try:
            result = fetch_categories(asset_type=asset_type)
            if "error" in result:
                raise Exception(result["error"])
            categories = result.get("categories", {})
            return format_categories_output(categories, asset_type)
        except Exception:
            blender = get_blender_connection()
            if not _polyhaven_enabled:
                return (
                    "PolyHaven integration is disabled. Select it in the sidebar in BlenderMCP, then run it again."
                )
            result = blender.send_command(
                "get_polyhaven_categories", {"asset_type": asset_type}
            )
            if "error" in result:
                return f"Error: {result['error']}"
            categories = result.get("categories", {})
            return format_categories_output(categories, asset_type)
    except Exception as e:
        logger.error(f"Error getting Polyhaven categories: {str(e)}")
        return f"Error getting Polyhaven categories: {str(e)}"


@mcp.tool()
def search_polyhaven_assets(
    ctx: Context[Any, Any, Any],
    asset_type: str = "all",
    categories: Optional[str] = None,
) -> str:
    try:
        # Try server-side search first
        try:
            result = search_assets_network(asset_type=asset_type, categories=categories)
            if not result:
                return "Error: Received no response from PolyHaven"
            if "error" in result:
                return f"Error: {result['error']}"
            return format_search_assets(result, categories)
        except Exception:
            blender = get_blender_connection()
            result = blender.send_command(
                "search_polyhaven_assets",
                {"asset_type": asset_type, "categories": categories},
            )

            if not result:
                return "Error: Received no response from Polyhaven"

            if "error" in result:
                return f"Error: {result['error']}"

            return format_search_assets(result, categories)
    except Exception as e:
        logger.error(f"Error searching Polyhaven assets: {str(e)}")
        return f"Error searching Polyhaven assets: {str(e)}"
    # Fallback for static analyzers: ensure a string is always returned
    return "Error searching Polyhaven assets"


@mcp.tool()
def download_polyhaven_asset(
    ctx: Context[Any, Any, Any],
    asset_id: str,
    asset_type: str,
    resolution: str = "1k",
    file_format: Optional[str] = None,
) -> str:
    try:
        # Try server-side helper first
        net_res = _server_download_asset(asset_id, asset_type, resolution, file_format)
        if net_res and net_res.get("temp_dir"):
            return f"Downloaded asset to temp dir: {net_res['temp_dir']}"

        # Fallback to addon-side download/import
        result = _addon_download_asset(asset_id, asset_type, resolution, file_format)
        if not result:
            return "Error: Received no response from Polyhaven download"
        if "error" in result:
            return f"Error: {result['error']}"

        return _format_addon_download_result(result, asset_type)
    except Exception as e:
        logger.error(f"Error downloading Polyhaven asset: {str(e)}")
        return f"Error downloading Polyhaven asset: {str(e)}"


def _server_download_asset(
    asset_id: str,
    asset_type: str,
    resolution: str,
    file_format: Optional[str],
) -> Optional[Dict[str, Any]]:
    try:
        return download_asset(
            asset_id=asset_id, asset_type=asset_type, resolution=resolution, file_format=file_format
        )
    except Exception:
        return None


def _addon_download_asset(
    asset_id: str,
    asset_type: str,
    resolution: str,
    file_format: Optional[str],
) -> Optional[Dict[str, Any]]:
    try:
        blender = get_blender_connection()
        return blender.send_command(
            "download_polyhaven_asset",
            {
                "asset_id": asset_id,
                "asset_type": asset_type,
                "resolution": resolution,
                "file_format": file_format,
            },
        )
    except Exception:
        return None


def _format_addon_download_result(result: Dict[str, Any], asset_type: str) -> str:
    if result.get("success"):
        message = result.get("message", "Asset downloaded and imported successfully")
        if asset_type == "hdris":
            return f"{message}. The HDRI has been set as the world environment."
        if asset_type == "textures":
            material_name = result.get("material", "")
            maps = ", ".join(result.get("maps", []))
            return f"{message}. Created material '{material_name}' with maps: {maps}."
        if asset_type == "models":
            return f"{message}. The model has been imported into the current scene."
        return message
    return f"Failed to download asset: {result.get('message', 'Unknown error')}"


@mcp.tool()
def set_texture(ctx: Context[Any, Any, Any], object_name: str, texture_id: str) -> str:
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "set_texture", {"object_name": object_name, "texture_id": texture_id}
        )
        if "error" in result:
            return f"Error: {result['error']}"
        if result.get("success"):
            material_name = result.get("material", "")
            maps = ", ".join(result.get("maps", []))
            material_info = result.get("material_info", {})
            node_count = material_info.get("node_count", 0)
            has_nodes = material_info.get("has_nodes", False)
            texture_nodes = material_info.get("texture_nodes", [])
            output = f"Successfully applied texture '{texture_id}' to {object_name}.\n"
            output += f"Using material '{material_name}' with maps: {maps}.\n\n"
            output += f"Material has nodes: {has_nodes}\n"
            output += f"Total node count: {node_count}\n\n"
            if texture_nodes:
                output += "Texture nodes:\n"
                for node in texture_nodes:
                    output += f"- {node['name']} using image: {node['image']}\n"
                    if node["connections"]:
                        output += "  Connections:\n"
                        for conn in node["connections"]:
                            output += f"    {conn}\n"
            else:
                output += "No texture nodes found in the material.\n"
            return output
        return f"Failed to apply texture: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error applying texture: {str(e)}")
        return f"Error applying texture: {str(e)}"


@mcp.tool()
def get_polyhaven_status(ctx: Context[Any, Any, Any]) -> str:
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_polyhaven_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += (
                "PolyHaven is strong for textures and has a wider "
                "variety of textures than Sketchfab."
            )
        return message
    except Exception as e:
        logger.error(f"Error checking PolyHaven status: {str(e)}")
        return f"Error checking PolyHaven status: {str(e)}"


@mcp.tool()
def get_hyper3d_status(ctx: Context[Any, Any, Any]) -> str:
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_hyper3d_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += ""
        return message
    except Exception as e:
        logger.error(f"Error checking Hyper3D status: {str(e)}")
        return f"Error checking Hyper3D status: {str(e)}"


@mcp.tool()
def get_sketchfab_status(ctx: Context[Any, Any, Any]) -> str:
    try:
        # Prefer server-side status check if an API key is configured
        api_key = os.environ.get("SKETCHFAB_API_KEY")
        if api_key:
            try:
                status = services_sketchfab.get_sketchfab_status(api_key)
                enabled = status.get("enabled", False)
                message = status.get("message", "")
                if enabled:
                    message += (
                        " Sketchfab is strong for realistic models and offers "
                        "a wider variety of models than PolyHaven."
                    )
                return message
            except Exception:
                # fallback to addon-side check
                pass

        blender = get_blender_connection()
        result = blender.send_command("get_sketchfab_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
                message += (
                    "Sketchfab is strong for realistic models and offers "
                    "a wider variety of models than PolyHaven."
                )
        return message
    except Exception as e:
        logger.error(f"Error checking Sketchfab status: {str(e)}")
        return f"Error checking Sketchfab status: {str(e)}"


@mcp.tool()
def search_sketchfab_models(
    ctx: Context[Any, Any, Any],
    query: str,
    categories: Optional[str] = None,
    count: int = 20,
    downloadable: bool = True,
) -> str:
    try:
        blender = get_blender_connection()
        msg = (
            "Searching Sketchfab models with query: %s, categories: %s, count: %s, "
            "downloadable: %s"
        )
        logger.info(msg, query, categories, count, downloadable)
        result = blender.send_command(
            "search_sketchfab_models",
            {
                "query": query,
                "categories": categories,
                "count": count,
                "downloadable": downloadable,
            },
        )
        if "error" in result:
            logger.error(f"Error from Sketchfab search: {result['error']}")
            return f"Error: {result['error']}"
        if result is None:
            logger.error("Received None result from Sketchfab search")
            return "Error: Received no response from Sketchfab search"
        models = result.get("results", []) or []
        if not models:
            return f"No models found matching '{query}'"
        formatted_output = f"Found {len(models)} models matching '{query}':\n\n"
        for model in models:
            if model is None:
                continue
            model_name = model.get("name", "Unnamed model")
            model_uid = model.get("uid", "Unknown ID")
            formatted_output += f"- {model_name} (UID: {model_uid})\n"
            user = model.get("user") or {}
            username = (
                user.get("username", "Unknown author")
                if isinstance(user, dict)
                else "Unknown author"
            )
            formatted_output += f"  Author: {username}\n"
            license_data = model.get("license") or {}
            license_label = (
                license_data.get("label", "Unknown")
                if isinstance(license_data, dict)
                else "Unknown"
            )
            formatted_output += f"  License: {license_label}\n"
            face_count = model.get("faceCount", "Unknown")
            is_downloadable = "Yes" if model.get("isDownloadable") else "No"
            formatted_output += f"  Face count: {face_count}\n"
            formatted_output += f"  Downloadable: {is_downloadable}\n\n"
        return formatted_output
    except Exception as e:
        logger.error(f"Error searching Sketchfab models: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return f"Error searching Sketchfab models: {str(e)}"


@mcp.tool()
def download_sketchfab_model(ctx: Context[Any, Any, Any], uid: str) -> str:
    try:
        blender = get_blender_connection()
        logger.info(f"Attempting to download Sketchfab model with UID: {uid}")
        result = blender.send_command("download_sketchfab_model", {"uid": uid})
        if result is None:
            logger.error("Received None result from Sketchfab download")
            return "Error: Received no response from Sketchfab download request"
        if "error" in result:
            logger.error(f"Error from Sketchfab download: {result['error']}")
            return f"Error: {result['error']}"
        if result.get("success"):
            imported_objects = result.get("imported_objects", [])
            object_names = ", ".join(imported_objects) if imported_objects else "none"
            return f"Successfully imported model. Created objects: {object_names}"
        return f"Failed to download model: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error downloading Sketchfab model: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return f"Error downloading Sketchfab model: {str(e)}"


@mcp.tool()
def generate_hyper3d_model_via_text(
    ctx: Context[Any, Any, Any],
    text_prompt: str,
    bbox_condition: Optional[List[float]] = None,
) -> str:
    try:
        blender = get_blender_connection()
        payload = prepare_rodin_payload(text_prompt, None, bbox_condition)
        result = blender.send_command("create_rodin_job", payload)
        succeed = result.get("submit_time", False)
        if succeed:
            return json.dumps(
                {
                    "task_uuid": result["uuid"],
                    "subscription_key": result["jobs"]["subscription_key"],
                }
            )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"


@mcp.tool()
def generate_hyper3d_model_via_images(
    ctx: Context[Any, Any, Any],
    input_image_paths: Optional[List[str]] = None,
    input_image_urls: Optional[List[str]] = None,
    bbox_condition: Optional[Sequence[float]] = None,
) -> str:
    if input_image_paths is not None and input_image_urls is not None:
        return "Error: Conflict parameters given!"
    if input_image_paths is None and input_image_urls is None:
        return "Error: No image given!"
    # images list may contain either (suffix, base64) tuples or url strings
    images: List[Union[Tuple[str, str], str]] = []

    if input_image_paths is not None:
        if not all(os.path.exists(i) for i in input_image_paths):
            return "Error: not all image paths are valid!"

        for path in input_image_paths:
            with open(path, "rb") as f:
                images.append(
                    (Path(path).suffix, base64.b64encode(f.read()).decode("ascii"))
                )
    elif input_image_urls is not None:
        # validate urls
        bad = [
            u
            for u in input_image_urls
            if not (urlparse(u).scheme and urlparse(u).netloc)
        ]
        if bad:
            return "Error: not all image URLs are valid!"

        images = cast(List[Union[Tuple[str, str], str]], input_image_urls.copy())
    try:
        blender = get_blender_connection()
        payload = prepare_rodin_payload(None, images, bbox_condition)
        result = blender.send_command("create_rodin_job", payload)
        succeed = result.get("submit_time", False)
        if succeed:
            return json.dumps(
                {
                    "task_uuid": result["uuid"],
                    "subscription_key": result["jobs"]["subscription_key"],
                }
            )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"


@mcp.tool()
def poll_rodin_job_status(
    ctx: Context[Any, Any, Any],
    subscription_key: Optional[str] = None,
    request_id: Optional[str] = None,
):
    try:
        blender = get_blender_connection()
        kwargs = {}
        if subscription_key:
            kwargs = {
                "subscription_key": subscription_key,
            }
        elif request_id:
            kwargs = {
                "request_id": request_id,
            }
        return blender.send_command("poll_rodin_job_status", kwargs)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"


@mcp.tool()
def import_generated_asset(
    ctx: Context[Any, Any, Any],
    name: str,
    task_uuid: Optional[str] = None,
    request_id: Optional[str] = None,
):
    try:
        blender = get_blender_connection()
        kwargs = {"name": name}
        if task_uuid:
            kwargs["task_uuid"] = task_uuid
        elif request_id:
            kwargs["request_id"] = request_id
        return blender.send_command("import_generated_asset", kwargs)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

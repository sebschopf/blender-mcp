"""Lightweight Hyper3D helpers.

This module intentionally remains small: it contains helpers that format
or validate input and can later be extended with network logic. For now it
re-exports the bbox helper so `integrations` can import from services.
"""

from typing import Any, Dict, List, Optional, Sequence

from blender_mcp import hyper3d as _h3d
from blender_mcp.errors import ExternalServiceError, InvalidParamsError
from blender_mcp.services.utils import process_bbox


def prepare_rodin_payload(
    text_prompt: Optional[str],
    images: Optional[List[Any]],
    bbox_condition: Optional[Sequence[float]],
) -> Dict[str, Any]:
    """Prepare a payload dict for submitting to a Rodin/Hyper3D job.

    This keeps payload shape in one place and is pure, so it's easy to
    unit-test.
    """
    return {
        "text_prompt": text_prompt,
        "images": images,
        "bbox_condition": process_bbox(bbox_condition),
    }


def generate_hyper3d_model_via_text(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = params or {}
    api_key = p.get("api_key")
    text_prompt = p.get("text_prompt")
    bbox_condition = p.get("bbox_condition")
    provider = p.get("provider", "fal_ai")

    if not isinstance(api_key, str) or not api_key:
        raise InvalidParamsError("missing or invalid 'api_key'")
    if not isinstance(text_prompt, str) or not text_prompt:
        raise InvalidParamsError("missing or invalid 'text_prompt'")
    try:
        if provider == "fal_ai":
            job = _h3d.create_rodin_job_fal_ai(
                api_key,
                text_prompt=text_prompt,
                images=None,
                bbox_condition=bbox_condition,
            )
        else:
            job = _h3d.create_rodin_job_main_site(
                api_key,
                text_prompt=text_prompt,
                images=None,
                bbox_condition=bbox_condition,
            )
        return {"status": "success", "result": job}
    except Exception as e:
        raise ExternalServiceError(str(e))


def generate_hyper3d_model_via_images(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = params or {}
    api_key = p.get("api_key")
    input_image_urls = p.get("input_image_urls")
    bbox_condition = p.get("bbox_condition")
    provider = p.get("provider", "fal_ai")

    if not isinstance(api_key, str) or not api_key:
        raise InvalidParamsError("missing or invalid 'api_key'")
    if (
        not isinstance(input_image_urls, list)
        or not input_image_urls
        or not all(isinstance(u, str) for u in input_image_urls)
    ):
        raise InvalidParamsError("'input_image_urls' must be a non-empty list of strings")
    try:
        if provider == "fal_ai":
            job = _h3d.create_rodin_job_fal_ai(api_key, images=input_image_urls, bbox_condition=bbox_condition)
        else:
            # main_site variant expects file tuples; not supported here
            raise InvalidParamsError("provider 'main_site' requires image file uploads; use 'fal_ai' with URLs")
        return {"status": "success", "result": job}
    except InvalidParamsError:
        raise
    except Exception as e:
        raise ExternalServiceError(str(e))


def poll_rodin_job_status(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = params or {}
    api_key = p.get("api_key")
    subscription_key = p.get("subscription_key")
    request_id = p.get("request_id")
    if not isinstance(api_key, str) or not api_key:
        raise InvalidParamsError("missing or invalid 'api_key'")
    if not isinstance(subscription_key, str) and not isinstance(request_id, str):
        raise InvalidParamsError("provide either 'subscription_key' (main_site) or 'request_id' (fal_ai)")
    try:
        if isinstance(request_id, str):
            res = _h3d.poll_rodin_job_status_fal_ai(api_key, request_id)
        else:
            assert isinstance(subscription_key, str)
            res = _h3d.poll_rodin_job_status_main_site(api_key, subscription_key)
        return {"status": "success", "result": res}
    except Exception as e:
        raise ExternalServiceError(str(e))


def import_generated_asset(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = params or {}
    api_key = p.get("api_key")
    name = p.get("name")
    task_uuid = p.get("task_uuid")
    request_id = p.get("request_id")
    if not isinstance(api_key, str) or not api_key:
        raise InvalidParamsError("missing or invalid 'api_key'")
    if not isinstance(name, str) or not name:
        raise InvalidParamsError("missing or invalid 'name'")
    if not isinstance(task_uuid, str) and not isinstance(request_id, str):
        raise InvalidParamsError("provide either 'task_uuid' (main_site) or 'request_id' (fal_ai)")
    try:
        if isinstance(request_id, str):
            res = _h3d.import_generated_asset_fal_ai(api_key, request_id, name)
        else:
            assert isinstance(task_uuid, str)
            res = _h3d.import_generated_asset_main_site(api_key, task_uuid, name)
        return {"status": "success", "result": res}
    except Exception as e:
        raise ExternalServiceError(str(e))

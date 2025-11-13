"""Helpers for interacting with Hyper3D / Rodin APIs.

These helpers centralize network requests and downloading so tests can mock
network I/O without importing the Blender addon.

Deprecated: utiliser ``blender_mcp.services.hyper3d`` pour une interface
service validée et des erreurs normalisées. Ce module est conservé pour
compatibilité transitoire et sera retiré dans un cycle futur.
"""

from __future__ import annotations

import json
import tempfile
import warnings as _warnings
from typing import Any, Dict, List, Optional, Tuple

import requests
import warnings as _warnings

_warnings.warn(
    "blender_mcp.hyper3d est déprécié; utiliser blender_mcp.services.hyper3d.",
    DeprecationWarning,
    stacklevel=2,
)

_warnings.warn(
    "blender_mcp.hyper3d est déprécié; utiliser blender_mcp.services.hyper3d.",
    DeprecationWarning,
    stacklevel=2,
)

from . import downloaders  # type: ignore


def create_rodin_job_main_site(
    api_key: str,
    text_prompt: Optional[str] = None,
    images: Optional[List[Tuple[str, Any]]] = None,
    bbox_condition: Optional[Dict[str, Any]] = None,
    session: Optional[requests.sessions.Session] = None,
) -> Dict[str, Any]:
    files: List[Tuple[str, Tuple[Optional[str], Any]]] = [
        *[("images", (f"{i:04d}{img_suffix}", img)) for i, (img_suffix, img) in enumerate(images or [])],
        ("tier", (None, "Sketch")),
        ("mesh_mode", (None, "Raw")),
    ]
    if text_prompt:
        files.append(("prompt", (None, text_prompt)))
    if bbox_condition:
        files.append(("bbox_condition", (None, json.dumps(bbox_condition))))

    headers = {"Authorization": f"Bearer {api_key}"}
    if session is None:
        # preserve backward-compatibility for tests that monkeypatch `requests.post`
        resp = requests.post("https://hyperhuman.deemos.com/api/v2/rodin", headers=headers, files=files)
    else:
        resp = session.post("https://hyperhuman.deemos.com/api/v2/rodin", headers=headers, files=files)
    return resp.json()


def create_rodin_job_fal_ai(
    api_key: str,
    text_prompt: Optional[str] = None,
    images: Optional[List[str]] = None,
    bbox_condition: Optional[Dict[str, Any]] = None,
    session: Optional[requests.sessions.Session] = None,
) -> Dict[str, Any]:
    req_data: Dict[str, Any] = {"tier": "Sketch"}
    if images:
        req_data["input_image_urls"] = images
    if text_prompt:
        req_data["prompt"] = text_prompt
    if bbox_condition:
        req_data["bbox_condition"] = bbox_condition

    headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
    if session is None:
        resp = requests.post("https://queue.fal.run/fal-ai/hyper3d/rodin", headers=headers, json=req_data)
    else:
        resp = session.post("https://queue.fal.run/fal-ai/hyper3d/rodin", headers=headers, json=req_data)
    return resp.json()


def poll_rodin_job_status_main_site(
    api_key: str, subscription_key: str, session: Optional[requests.sessions.Session] = None
) -> Dict[str, Any]:
    if session is None:
        resp = requests.post(
            "https://hyperhuman.deemos.com/api/v2/status",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"subscription_key": subscription_key},
        )
    else:
        resp = session.post(
            "https://hyperhuman.deemos.com/api/v2/status",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"subscription_key": subscription_key},
        )
    data = resp.json()
    return {"status_list": [i["status"] for i in data.get("jobs", [])]}


def poll_rodin_job_status_fal_ai(
    api_key: str, request_id: str, session: Optional[requests.sessions.Session] = None
) -> Dict[str, Any]:
    if session is None:
        resp = requests.get(
            f"https://queue.fal.run/fal-ai/hyper3d/requests/{request_id}/status",
            headers={"Authorization": f"KEY {api_key}"},
        )
    else:
        resp = session.get(
            f"https://queue.fal.run/fal-ai/hyper3d/requests/{request_id}/status",
            headers={"Authorization": f"KEY {api_key}"},
        )
    return resp.json()


def import_generated_asset_main_site(
    api_key: str, task_uuid: str, name: str, session: Optional[requests.sessions.Session] = None
) -> Dict[str, Any]:
    if session is None:
        resp = requests.post(
            "https://hyperhuman.deemos.com/api/v2/download",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"task_uuid": task_uuid},
        )
    else:
        resp = session.post(
            "https://hyperhuman.deemos.com/api/v2/download",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"task_uuid": task_uuid},
        )
    data_ = resp.json()

    temp_file_path: Optional[str] = None
    for i in data_.get("list", []):
        if i.get("name", "").endswith(".glb"):
            url = i.get("url")
            try:
                # Prefer centralized downloader but only forward the `session`
                # argument when the caller provided one. This keeps tests that
                # monkeypatch `download_bytes` without a `session` kw working.
                if session is None:
                    content = downloaders.download_bytes(url, timeout=120)
                else:
                    content = downloaders.download_bytes(url, timeout=120, session=session)
                tf = tempfile.NamedTemporaryFile(delete=False, prefix=task_uuid, suffix=".glb")
                tf.write(content)
                tf.close()
                temp_file_path = tf.name
            except Exception:
                # Fallback to streaming requests
                if session is None:
                    r = requests.get(url, stream=True)
                else:
                    r = session.get(url, stream=True)
                r.raise_for_status()
                tf = tempfile.NamedTemporaryFile(delete=False, prefix=task_uuid, suffix=".glb")
                for chunk in r.iter_content(chunk_size=8192):
                    tf.write(chunk)
                tf.close()
                temp_file_path = tf.name
            break

    if not temp_file_path:
        return {"succeed": False, "error": "No glb found in download list"}

    # Return minimal result; importing into Blender is the addon's responsibility
    return {"succeed": True, "temp_file": temp_file_path, "name": name}


def import_generated_asset_fal_ai(
    api_key: str, request_id: str, name: str, session: Optional[requests.sessions.Session] = None
) -> Dict[str, Any]:
    if session is None:
        url = f"https://queue.fal.run/fal-ai/hyper3d/requests/{request_id}"
        headers = {"Authorization": f"Key {api_key}"}
        resp = requests.get(url, headers=headers)
    else:
        url = f"https://queue.fal.run/fal-ai/hyper3d/requests/{request_id}"
        headers = {"Authorization": f"Key {api_key}"}
        resp = session.get(url, headers=headers)
    data_ = resp.json()
    url = data_.get("model_mesh", {}).get("url")
    if not url:
        return {"succeed": False, "error": "No model URL in response"}

    try:
        if session is None:
            content = downloaders.download_bytes(url, timeout=120)
        else:
            content = downloaders.download_bytes(url, timeout=120, session=session)
        tf = tempfile.NamedTemporaryFile(delete=False, prefix=request_id, suffix=".glb")
        tf.write(content)
        tf.close()
        return {"succeed": True, "temp_file": tf.name, "name": name}
    except Exception as e:
        return {"succeed": False, "error": str(e)}

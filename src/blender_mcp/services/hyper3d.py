"""Lightweight Hyper3D helpers.

This module intentionally remains small: it contains helpers that format
or validate input and can later be extended with network logic. For now it
re-exports the bbox helper so `integrations` can import from services.
"""
from typing import Any, Dict, List, Optional, Sequence

from .utils import process_bbox


def prepare_rodin_payload(
    text_prompt: Optional[str], images: Optional[List[Any]], bbox_condition: Optional[Sequence[float]]
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

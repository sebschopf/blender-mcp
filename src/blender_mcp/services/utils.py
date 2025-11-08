"""Utility helpers used by service modules.

Keep pure, well-typed helpers here so they can be unit-tested.
"""
from typing import List, Optional, Sequence


def process_bbox(original_bbox: Optional[Sequence[float]] = None) -> Optional[List[int]]:
    """Normalize a bbox (sequence of numbers) into percentages as ints or return None.

    This is a small, pure helper extracted from integrations to make it
    easily testable and reusable by Hyper3D/PolyHaven helpers.
    """
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

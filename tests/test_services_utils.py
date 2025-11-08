import pytest

from blender_mcp.services.utils import process_bbox


def test_process_bbox_happy_path():
    assert process_bbox([1, 2, 3]) == [33, 66, 100]


def test_process_bbox_none():
    assert process_bbox(None) is None


def test_process_bbox_invalid_values():
    with pytest.raises(ValueError):
        process_bbox([0, 0, 0])

    with pytest.raises(ValueError):
        process_bbox([-1, 2, 3])

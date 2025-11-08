import pytest

from blender_mcp.server import _process_bbox


def test_process_bbox_none():
    assert _process_bbox(None) is None


def test_process_bbox_ints():
    assert _process_bbox([2, 2, 1]) == [100, 100, 50]


def test_process_bbox_floats():
    assert _process_bbox([0.5, 1.0, 0.25]) == [50, 100, 25]


def test_process_bbox_zero_max_raises():
    with pytest.raises(ValueError):
        _process_bbox([0, 0, 0])


def test_process_bbox_negative_raises():
    with pytest.raises(ValueError):
        _process_bbox([1, -1, 2])

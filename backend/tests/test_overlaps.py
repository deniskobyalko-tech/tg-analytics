"""Tests for forward-graph audience overlap computation."""

from app.workers.compute_overlaps import compute_forward_overlap


def test_forward_overlap_shared():
    # Channel A forwards from X, Y, Z
    # Channel B forwards from Y, Z, W
    # Jaccard: |{Y,Z}| / |{X,Y,Z,W}| = 2/4 = 0.5
    forwards_a = {"x", "y", "z"}
    forwards_b = {"y", "z", "w"}
    assert compute_forward_overlap(forwards_a, forwards_b) == 0.5


def test_forward_overlap_none():
    assert compute_forward_overlap(set(), set()) == 0.0


def test_forward_overlap_no_intersection():
    assert compute_forward_overlap({"a", "b"}, {"c", "d"}) == 0.0


def test_forward_overlap_identical():
    assert compute_forward_overlap({"a", "b", "c"}, {"a", "b", "c"}) == 1.0


def test_forward_overlap_one_empty():
    assert compute_forward_overlap({"a", "b"}, set()) == 0.0

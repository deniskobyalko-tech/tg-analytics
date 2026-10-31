"""Tests for category benchmarks."""

from app.workers.compute_benchmarks import calculate_category_averages


def test_calculate_averages():
    channels = [
        {"subscribers_count": 1000, "er": 5.0, "avg_views": 500, "posts_per_week": 7.0},
        {"subscribers_count": 3000, "er": 3.0, "avg_views": 900, "posts_per_week": 3.0},
    ]
    result = calculate_category_averages(channels)
    assert result["avg_subscribers"] == 2000
    assert result["avg_er"] == 4.0
    assert result["avg_views"] == 700
    assert result["avg_posts_per_week"] == 5.0
    assert result["channel_count"] == 2


def test_calculate_averages_empty():
    result = calculate_category_averages([])
    assert result["avg_subscribers"] == 0
    assert result["channel_count"] == 0


def test_calculate_averages_single():
    channels = [{"subscribers_count": 5000, "er": 10.0, "avg_views": 2000, "posts_per_week": 5.0}]
    result = calculate_category_averages(channels)
    assert result["avg_subscribers"] == 5000
    assert result["channel_count"] == 1

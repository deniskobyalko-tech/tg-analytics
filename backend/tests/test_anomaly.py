"""Tests for anomaly detection functions."""

from datetime import datetime, timedelta, timezone

from app.services.anomaly import (
    detect_er_drop,
    detect_inactive,
    detect_subscriber_drop,
    detect_subscriber_spike,
)


def test_subscriber_spike():
    assert detect_subscriber_spike(before=1000, after=1200) is True  # +20%
    assert detect_subscriber_spike(before=1000, after=1050) is False  # +5%
    assert detect_subscriber_spike(before=0, after=100) is False


def test_subscriber_drop():
    assert detect_subscriber_drop(before=1000, after=900) is True  # -10%
    assert detect_subscriber_drop(before=1000, after=980) is False  # -2%
    assert detect_subscriber_drop(before=0, after=0) is False


def test_er_drop():
    assert detect_er_drop(current_er=3.0, avg_er_7d=5.0) is True  # -40%
    assert detect_er_drop(current_er=4.5, avg_er_7d=5.0) is False  # -10%
    assert detect_er_drop(current_er=5.0, avg_er_7d=0) is False


def test_detect_inactive():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=5)
    old = now - timedelta(days=35)
    very_old = now - timedelta(days=100)

    assert detect_inactive(recent) == "active"
    assert detect_inactive(old) == "inactive"
    assert detect_inactive(very_old) == "dead"
    assert detect_inactive(None) == "active"

"""Tests for extended stats orchestrator."""

from datetime import datetime, timedelta, timezone

from app.services.extended_stats import is_cache_fresh


def test_cache_fresh():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(minutes=30)
    assert is_cache_fresh(recent) is True


def test_cache_stale():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(hours=2)
    assert is_cache_fresh(old) is False


def test_cache_none():
    assert is_cache_fresh(None) is False

"""Anomaly detection functions for channel metrics."""

from datetime import datetime, timezone


def detect_subscriber_spike(before: int, after: int, threshold: float = 0.10) -> bool:
    """Return True if subscriber growth exceeds threshold (default 10%)."""
    if before == 0:
        return False
    return (after - before) / before > threshold


def detect_subscriber_drop(before: int, after: int, threshold: float = 0.05) -> bool:
    """Return True if subscriber loss exceeds threshold (default 5%)."""
    if before == 0:
        return False
    return (before - after) / before > threshold


def detect_er_drop(current_er: float, avg_er_7d: float, threshold: float = 0.30) -> bool:
    """Return True if ER dropped more than threshold vs 7-day average."""
    if avg_er_7d == 0:
        return False
    return (avg_er_7d - current_er) / avg_er_7d > threshold


def detect_inactive(last_post_date: datetime | None, inactive_days: int = 30, dead_days: int = 90) -> str:
    """Return channel status based on last post date."""
    if last_post_date is None:
        return "active"
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if last_post_date.tzinfo is not None:
        last_post_date = last_post_date.replace(tzinfo=None)
    age = (now - last_post_date).days
    if age >= dead_days:
        return "dead"
    if age >= inactive_days:
        return "inactive"
    return "active"

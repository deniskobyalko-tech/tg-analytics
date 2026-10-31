"""Periodic worker: detect anomalies in channel metrics and create alerts."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.core.database import async_session
from app.models.alert import AnomalyAlert
from app.models.channel import Channel, ChannelSnapshot
from app.services.anomaly import detect_er_drop, detect_subscriber_drop, detect_subscriber_spike

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def detect_all_anomalies() -> None:
    """Check all tracked channels for anomalies."""
    async with async_session() as db:
        result = await db.execute(
            select(Channel).where(Channel.is_tracked.is_(True))
        )
        channels = result.scalars().all()

        for ch in channels:
            try:
                await _check_channel(db, ch)
            except Exception as e:
                logger.error("Anomaly check failed for %s: %s", ch.username, e)

        await db.commit()
        logger.info("Anomaly detection completed for %d tracked channels", len(channels))


async def _check_channel(db, ch: Channel) -> None:
    """Check a single channel for anomalies."""
    # Get yesterday's snapshot for comparison
    yesterday = (_utcnow() - timedelta(days=1)).date()
    snap_result = await db.execute(
        select(ChannelSnapshot).where(
            ChannelSnapshot.channel_id == ch.id,
            ChannelSnapshot.date == yesterday,
        )
    )
    prev_snap = snap_result.scalar_one_or_none()
    if prev_snap is None:
        return

    # Subscriber spike
    if detect_subscriber_spike(prev_snap.subscribers, ch.subscribers_count):
        await _create_alert(
            db, ch.id, "subscriber_spike",
            f"@{ch.username}: subscribers +{ch.subscribers_count - prev_snap.subscribers} "
            f"({prev_snap.subscribers} → {ch.subscribers_count})",
            prev_snap.subscribers, ch.subscribers_count,
        )

    # Subscriber drop
    if detect_subscriber_drop(prev_snap.subscribers, ch.subscribers_count):
        await _create_alert(
            db, ch.id, "subscriber_drop",
            f"@{ch.username}: subscribers -{prev_snap.subscribers - ch.subscribers_count} "
            f"({prev_snap.subscribers} → {ch.subscribers_count})",
            prev_snap.subscribers, ch.subscribers_count,
        )

    # ER drop vs 7-day average
    week_ago = (_utcnow() - timedelta(days=7)).date()
    er_result = await db.execute(
        select(func.avg(ChannelSnapshot.er)).where(
            ChannelSnapshot.channel_id == ch.id,
            ChannelSnapshot.date >= week_ago,
        )
    )
    avg_er_7d = er_result.scalar() or 0
    if detect_er_drop(ch.er, avg_er_7d):
        await _create_alert(
            db, ch.id, "er_drop",
            f"@{ch.username}: ER dropped to {ch.er}% (7d avg: {avg_er_7d:.1f}%)",
            avg_er_7d, ch.er,
        )


async def _create_alert(
    db, channel_id: int, alert_type: str, message: str,
    value_before: float, value_after: float,
) -> None:
    """Create alert if no duplicate exists in last 24h."""
    day_ago = _utcnow() - timedelta(hours=24)
    existing = await db.execute(
        select(AnomalyAlert).where(
            AnomalyAlert.channel_id == channel_id,
            AnomalyAlert.alert_type == alert_type,
            AnomalyAlert.created_at >= day_ago,
        )
    )
    if existing.scalar_one_or_none() is not None:
        return  # deduplicate

    db.add(AnomalyAlert(
        channel_id=channel_id,
        alert_type=alert_type,
        message=message,
        value_before=value_before,
        value_after=value_after,
    ))
    logger.warning("Alert: %s", message)

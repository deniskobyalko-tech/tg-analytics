"""Anomaly alerts API."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.alert import AnomalyAlert
from app.models.channel import Channel
from app.schemas.common import ApiResponse, PaginationMeta

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
async def get_alerts(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Get recent anomaly alerts for all tracked channels."""
    limit = min(limit, 100)

    from sqlalchemy import func
    total = (await db.execute(
        select(func.count()).select_from(AnomalyAlert)
    )).scalar() or 0

    offset = (page - 1) * limit
    result = await db.execute(
        select(AnomalyAlert, Channel.username)
        .join(Channel, Channel.id == AnomalyAlert.channel_id)
        .order_by(AnomalyAlert.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = result.all()

    data = [
        {
            "id": row.AnomalyAlert.id,
            "channel_username": row.username,
            "alert_type": row.AnomalyAlert.alert_type,
            "message": row.AnomalyAlert.message,
            "value_before": row.AnomalyAlert.value_before,
            "value_after": row.AnomalyAlert.value_after,
            "created_at": row.AnomalyAlert.created_at.isoformat(),
        }
        for row in rows
    ]
    return ApiResponse(
        success=True,
        data=data,
        meta=PaginationMeta(total=total, page=page, limit=limit),
    )


@router.get("/{username}")
async def get_channel_alerts(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Get alerts for a specific channel."""
    username = username.lstrip("@").lower()
    result = await db.execute(select(Channel).where(Channel.username == username))
    channel = result.scalar_one_or_none()
    if channel is None:
        return ApiResponse(success=False, error="Channel not found")

    alerts_result = await db.execute(
        select(AnomalyAlert)
        .where(AnomalyAlert.channel_id == channel.id)
        .order_by(AnomalyAlert.created_at.desc())
        .limit(50)
    )
    alerts = alerts_result.scalars().all()

    data = [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "message": a.message,
            "value_before": a.value_before,
            "value_after": a.value_after,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]
    return ApiResponse(success=True, data=data)

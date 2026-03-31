from datetime import datetime, timezone
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ChannelSimilarity(Base):
    __tablename__ = "channel_similarities"
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), primary_key=True)
    similar_channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), primary_key=True)
    score: Mapped[float] = mapped_column(Float)
    match_type: Mapped[str] = mapped_column(String(20))


class AudienceOverlap(Base):
    __tablename__ = "audience_overlaps"
    channel_a_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), primary_key=True)
    channel_b_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), primary_key=True)
    overlap_percent: Mapped[float] = mapped_column(Float)
    calculated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

from datetime import date, datetime, timezone
from sqlalchemy import BigInteger, Date, Float, ForeignKey, String, UniqueConstraint


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Channel(Base):
    __tablename__ = "channels"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(default=None)
    avatar_url: Mapped[str | None] = mapped_column(String(500), default=None)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("channel_categories.id"), default=None)
    language: Mapped[str | None] = mapped_column(String(5), default=None)
    subscribers_count: Mapped[int] = mapped_column(default=0)
    avg_views: Mapped[int] = mapped_column(default=0)
    er: Mapped[float] = mapped_column(Float, default=0.0)
    posts_per_week: Mapped[float] = mapped_column(Float, default=0.0)
    is_tracked: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=_utcnow, onupdate=_utcnow)
    last_scraped_at: Mapped[datetime | None] = mapped_column(default=None)
    last_telethon_at: Mapped[datetime | None] = mapped_column(default=None)
    snapshots: Mapped[list["ChannelSnapshot"]] = relationship(back_populates="channel")


class ChannelSnapshot(Base):
    __tablename__ = "channel_snapshots"
    __table_args__ = (UniqueConstraint("channel_id", "date"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    date: Mapped[date] = mapped_column(Date)
    subscribers: Mapped[int] = mapped_column(default=0)
    avg_views: Mapped[int] = mapped_column(default=0)
    er: Mapped[float] = mapped_column(Float, default=0.0)
    posts_count: Mapped[int] = mapped_column(default=0)
    channel: Mapped["Channel"] = relationship(back_populates="snapshots")

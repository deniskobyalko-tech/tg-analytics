from datetime import datetime, timezone
from sqlalchemy import BigInteger, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("channel_id", "telegram_post_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    telegram_post_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[str | None] = mapped_column(default=None)
    date: Mapped[datetime] = mapped_column()
    views: Mapped[int] = mapped_column(default=0)
    forwards: Mapped[int] = mapped_column(default=0)
    reactions: Mapped[int] = mapped_column(default=0)
    comments_count: Mapped[int] = mapped_column(default=0)
    is_ad: Mapped[bool] = mapped_column(default=False)
    ad_price: Mapped[float | None] = mapped_column(Float, default=None)
    fwd_from_channel: Mapped[str | None] = mapped_column(String(100), default=None)
    updated_at: Mapped[datetime] = mapped_column(default=_utcnow, onupdate=_utcnow)

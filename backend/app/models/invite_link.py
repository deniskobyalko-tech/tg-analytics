from datetime import datetime, timezone
from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ChannelInviteLink(Base):
    __tablename__ = "channel_invite_links"
    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    link: Mapped[str] = mapped_column(String(255))
    creator_id: Mapped[int | None] = mapped_column(BigInteger, default=None)
    usage_count: Mapped[int] = mapped_column(default=0)
    fetched_at: Mapped[datetime] = mapped_column(default=_utcnow)

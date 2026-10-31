from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ChannelMember(Base):
    __tablename__ = "channel_members"
    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    telegram_user_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str | None] = mapped_column(String(100), default=None)
    first_name: Mapped[str | None] = mapped_column(String(255), default=None)
    joined_at: Mapped[datetime | None] = mapped_column(default=None)
    left_at: Mapped[datetime | None] = mapped_column(default=None)

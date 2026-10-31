from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ChannelAdminLog(Base):
    __tablename__ = "channel_admin_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    event_type: Mapped[str] = mapped_column(String(30))
    user_id: Mapped[int] = mapped_column(BigInteger)
    data: Mapped[dict | None] = mapped_column(JSON, default=None)
    event_date: Mapped[datetime] = mapped_column()

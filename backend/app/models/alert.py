from datetime import datetime, timezone
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AnomalyAlert(Base):
    __tablename__ = "anomaly_alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    alert_type: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column()
    value_before: Mapped[float] = mapped_column(Float)
    value_after: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    is_sent: Mapped[bool] = mapped_column(default=False)

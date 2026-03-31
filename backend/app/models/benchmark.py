from datetime import UTC, date, datetime
from sqlalchemy import Date, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class CategoryBenchmark(Base):
    __tablename__ = "category_benchmarks"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("channel_categories.id"))
    date: Mapped[date] = mapped_column(Date)
    avg_subscribers: Mapped[int] = mapped_column(default=0)
    avg_er: Mapped[float] = mapped_column(Float, default=0.0)
    avg_views: Mapped[int] = mapped_column(default=0)
    avg_posts_per_week: Mapped[float] = mapped_column(Float, default=0.0)
    channel_count: Mapped[int] = mapped_column(default=0)

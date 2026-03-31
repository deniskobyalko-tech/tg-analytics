from datetime import datetime
from pydantic import BaseModel, field_validator


class ChannelAnalyzeRequest(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def clean_username(cls, v: str) -> str:
        v = v.strip()
        if v.startswith("@"):
            v = v[1:]
        if v.startswith("https://t.me/"):
            v = v.replace("https://t.me/", "")
        if v.startswith("t.me/"):
            v = v.replace("t.me/", "")
        return v.lower()


class ChannelOut(BaseModel):
    id: int
    telegram_id: int
    username: str
    title: str
    description: str | None = None
    avatar_url: str | None = None
    category: str | None = None
    subscribers_count: int
    avg_views: int
    er: float
    posts_per_week: float
    last_scraped_at: datetime | None = None
    model_config = {"from_attributes": True}


class ChannelSnapshotOut(BaseModel):
    date: datetime
    subscribers: int
    avg_views: int
    er: float
    posts_count: int
    model_config = {"from_attributes": True}

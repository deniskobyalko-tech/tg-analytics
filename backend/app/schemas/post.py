from datetime import datetime
from pydantic import BaseModel


class PostOut(BaseModel):
    id: int
    telegram_post_id: int
    text: str | None = None
    date: datetime
    views: int
    forwards: int
    reactions: int
    is_ad: bool
    ad_price: float | None = None
    model_config = {"from_attributes": True}

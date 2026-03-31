from typing import Any
from pydantic import BaseModel


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int


class ApiResponse(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None
    meta: PaginationMeta | None = None

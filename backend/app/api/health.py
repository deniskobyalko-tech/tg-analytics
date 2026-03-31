from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass
    status = "ok" if db_ok else "degraded"
    return {
        "success": True,
        "data": {"status": status, "database": db_ok},
        "error": None,
        "meta": None,
    }

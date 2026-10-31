import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.alerts import router as alerts_router
from app.api.benchmarks import router as benchmarks_router
from app.api.catalog import router as catalog_router
from app.api.channels import router as channels_router
from app.api.compare import router as compare_router
from app.api.export import router as export_router
from app.api.health import router as health_router
from app.api.search import router as search_router
from app.api.watchlist import router as watchlist_router
from app.api.ws import router as ws_router
from app.workers.bot_polling import start_bot_polling
from app.workers.scheduler import start_scheduler
from app.workers.seed_categories import seed_categories


@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_categories()
    start_scheduler()
    bot_task = asyncio.create_task(start_bot_polling())
    yield
    bot_task.cancel()


app = FastAPI(title="TG Channel Analytics", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(channels_router, prefix="/api")
app.include_router(compare_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(watchlist_router, prefix="/api")
app.include_router(benchmarks_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(ws_router)

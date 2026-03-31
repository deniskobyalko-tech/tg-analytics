from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.channels import router as channels_router
from app.api.health import router as health_router
from app.workers.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield


app = FastAPI(title="TG Channel Analytics", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(channels_router, prefix="/api")

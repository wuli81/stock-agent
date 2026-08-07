"""FastAPI 应用入口。

启动：
    uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()
setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.scheduler.jobs import start_scheduler

    start_scheduler()
    yield


app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)
app.include_router(api_router, prefix=settings.api_prefix)

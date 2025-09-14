from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.endpoints import search
from app.core.config import settings
from app.core.cache import cache

logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ТОЛЬКО поисковый энд-поинт
app.include_router(search.router, tags=["search"])


@app.on_event("startup")
async def startup():
    await cache.connect()


@app.on_event("shutdown")
async def shutdown():
    await cache.disconnect()
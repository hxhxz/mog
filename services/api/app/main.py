from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.ws_manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await ws_manager.start()
    yield
    await ws_manager.stop()


app = FastAPI(
    title="mog API",
    version="0.1.0",
    description="AI short drama video generation platform — backend API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "api"}

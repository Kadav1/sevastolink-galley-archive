import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Make packages/shared-prompts importable without a formal pip install.
# The repo is always present at REPO_ROOT (volume-mounted or local clone).
_SHARED_PROMPTS_SRC = str(Path(__file__).resolve().parents[3] / "packages" / "shared-prompts" / "src")
if _SHARED_PROMPTS_SRC not in sys.path:
    sys.path.insert(0, _SHARED_PROMPTS_SRC)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.routing import APIRouter

import src.models  # noqa: F401 — registers all ORM models for FK resolution
from src.config.settings import settings
from src.db.init_db import init_db
from src.routes.health import router as health_router
from src.routes.intake import router as intake_router
from src.routes.media import router as media_router
from src.routes.pantry import router as pantry_router
from src.routes.recipes import router as recipes_router
from src.routes.settings import router as settings_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Galley API starting — initialising database")
    init_db()
    logger.info("Database ready")
    yield
    logger.info("Galley API shutting down")


app = FastAPI(
    title="Galley Archive API",
    description="Sevastolink Galley Archive — local recipe archive service",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(recipes_router)
v1_router.include_router(intake_router)
v1_router.include_router(media_router)
v1_router.include_router(pantry_router)
v1_router.include_router(settings_router)
app.include_router(v1_router)

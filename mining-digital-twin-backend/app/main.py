"""
FastAPI Application Entry Point
Ore Beneficiation Plant Digital Twin - Backend
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import plant, equipment, streams, simulation, analytics, optimization
from app.mock.seed_data import get_current_state

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up simulation state on startup
    logger.info("Initialising digital-twin state (DEMO mode = %s)...", settings.demo_mode)
    get_current_state()
    logger.info("Digital-twin state ready.")
    yield
    logger.info("Backend shutting down.")


app = FastAPI(
    title="Ore Beneficiation Digital Twin API",
    description=(
        "FastAPI backend for the Ore Beneficiation Plant Digital Twin. "
        "All data is DEMO/SIMULATION unless a live data source is configured."
    ),
    version=settings.model_version,
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────────────────────────────────────
app.include_router(plant.router)
app.include_router(equipment.router)
app.include_router(streams.router)
app.include_router(simulation.router)
app.include_router(analytics.router)
app.include_router(optimization.router)


@app.get("/")
def root():
    return {
        "service": "Ore Beneficiation Digital Twin Backend",
        "version": settings.model_version,
        "mode": "DEMO" if settings.demo_mode else settings.app_env,
        "docs": "/docs",
        "health": "/health",
    }

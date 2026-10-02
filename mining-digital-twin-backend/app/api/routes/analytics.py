"""API Routes: /api/v1/analytics"""
from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas.domain import MassBalanceSchema
from app.mock.seed_data import get_current_state
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/mass-balance", response_model=MassBalanceSchema)
def get_mass_balance():
    state = get_current_state()
    return state.mass_balance


@router.get("/trends")
def get_trends() -> Dict[str, Any]:
    """Return simulated trend data (last 24 h) for key KPIs."""
    import numpy as np
    rng = np.random.default_rng(42)
    hours = list(range(0, 25))
    state = get_current_state()
    base_feed = state.inputs.feed_rate_tph

    feed_trend = [round(float(base_feed * (1 + rng.uniform(-0.05, 0.05))), 1) for _ in hours]
    recovery_trend = [round(float(72 + rng.uniform(-3, 3)), 2) for _ in hours]
    closure_trend = [round(float(96 + rng.uniform(-2, 2)), 2) for _ in hours]
    water_trend = [round(float(200 + rng.uniform(-20, 20)), 1) for _ in hours]

    return {
        "mode": "DEMO",
        "disclaimer": "Simulated trend data — not real plant historian data.",
        "timestamps": [f"T-{24 - h}h" for h in hours],
        "feed_rate_tph": feed_trend,
        "recovery_pct": recovery_trend,
        "mass_balance_closure_pct": closure_trend,
        "water_usage_m3h": water_trend,
    }

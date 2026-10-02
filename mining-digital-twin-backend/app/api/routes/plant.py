"""API Routes: /health and /api/v1/plant/overview"""
from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas.domain import PlantOverviewSchema, PlantSchema, DataMode, EquipmentStatus
from app.mock.seed_data import (
    get_current_state, build_alarms, build_data_quality, get_scenarios
)

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "OK", "timestamp": datetime.now(timezone.utc).isoformat(), "version": "1.0.0"}


@router.get("/api/v1/plant/overview", response_model=PlantOverviewSchema)
def plant_overview():
    state = get_current_state()
    eq_list = list(state.equipment_states.values())
    status_counts: dict[str, int] = {}
    for eq in eq_list:
        status_counts[eq.status.value] = status_counts.get(eq.status.value, 0) + 1

    feed = state.inputs.feed_rate_tph
    products = state.mass_balance.product_tph
    product_total = sum(products.values())
    recovery = (product_total / feed * 100) if feed > 0 else 0.0
    alarms = build_alarms()
    dq = build_data_quality(state.stream_states)

    plant = PlantSchema(
        timestamp=state.timestamp,
        mode=DataMode.DEMO,
        overall_status=EquipmentStatus.SIMULATION,
        feed_rate_tph=feed,
        product_rates=products,
        water_usage_m3h=state.inputs.water_addition_m3h,
        recovery_pct=round(recovery, 2),
        mass_balance_closure_pct=round(state.mass_balance.closure_pct, 2),
        active_alarms=sum(1 for a in alarms if not a.acknowledged),
    )

    return PlantOverviewSchema(
        plant=plant,
        equipment_summary=status_counts,
        active_alarms=alarms,
        recent_scenarios=get_scenarios()[:5],
        data_quality=dq,
    )

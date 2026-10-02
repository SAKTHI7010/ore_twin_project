"""API Routes: /api/v1/optimization and /api/v1/data-quality"""
from fastapi import APIRouter
from app.schemas.domain import OptimizationRequest, OptimizationResult, DataQualitySchema, SimulationInputs
from app.mock.seed_data import get_current_state, build_data_quality

router = APIRouter(tags=["optimization", "data_quality"])


@router.post("/api/v1/optimization/run", response_model=OptimizationResult)
def run_optimization(req: OptimizationRequest):
    """
    Demo advisory optimization — clearly labeled, not a real control command.
    """
    state = get_current_state()
    # Simple heuristic: nudge inputs toward higher recovery
    recommended = SimulationInputs(
        feed_rate_tph=state.inputs.feed_rate_tph * 0.95,
        feed_moisture_pct=state.inputs.feed_moisture_pct,
        water_addition_m3h=state.inputs.water_addition_m3h * 1.05,
        primary_crusher_css_mm=max(120, state.inputs.primary_crusher_css_mm - 10),
        secondary_crusher_css_mm=max(60, state.inputs.secondary_crusher_css_mm - 5),
        scrubber_water_m3h=state.inputs.scrubber_water_m3h * 1.10,
        jig_water_m3h=state.inputs.jig_water_m3h * 1.05,
        cyclone_pressure_kpa=min(150, state.inputs.cyclone_pressure_kpa + 10),
    )
    return OptimizationResult(
        objective=req.objective,
        recommended_inputs=recommended,
        expected_recovery_pct=round(state.mass_balance.closure_pct * 0.78, 2),
        expected_throughput_tph=round(recommended.feed_rate_tph, 1),
        advisory_notes=[
            "Reduce feed rate by ~5% to improve classification efficiency.",
            "Increase scrubber water by 10% to enhance liberation.",
            "Lower primary CSS by 10 mm for finer primary product.",
            "All values are DEMO — validate with plant engineer before any operational change.",
        ],
    )


@router.get("/api/v1/data-quality", response_model=DataQualitySchema)
def get_data_quality():
    state = get_current_state()
    return build_data_quality(state.stream_states)

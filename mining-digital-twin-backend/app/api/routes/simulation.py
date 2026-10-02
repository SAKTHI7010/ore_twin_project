"""API Routes: /api/v1/simulation"""
from fastapi import APIRouter
from app.schemas.domain import SimulationStateSchema, SimulationInputs
from app.mock.seed_data import get_current_state, run_simulation

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])


@router.get("/state", response_model=SimulationStateSchema)
def get_simulation_state():
    return get_current_state()


@router.post("/run", response_model=SimulationStateSchema)
def run_simulation_step(inputs: SimulationInputs):
    return run_simulation(inputs)

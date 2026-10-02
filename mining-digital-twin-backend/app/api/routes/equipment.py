"""API Routes: /api/v1/equipment"""
from fastapi import APIRouter, HTTPException
from app.schemas.domain import EquipmentSchema
from app.mock.seed_data import get_current_state
from typing import List

router = APIRouter(prefix="/api/v1/equipment", tags=["equipment"])


@router.get("", response_model=List[EquipmentSchema])
def list_equipment():
    state = get_current_state()
    return list(state.equipment_states.values())


@router.get("/{equipment_id}", response_model=EquipmentSchema)
def get_equipment(equipment_id: str):
    state = get_current_state()
    eq = state.equipment_states.get(equipment_id)
    if not eq:
        raise HTTPException(status_code=404, detail=f"Equipment '{equipment_id}' not found")
    return eq

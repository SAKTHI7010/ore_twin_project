"""API Routes: /api/v1/streams"""
from fastapi import APIRouter, HTTPException
from app.schemas.domain import StreamSchema
from app.mock.seed_data import get_current_state
from typing import List

router = APIRouter(prefix="/api/v1/streams", tags=["streams"])


@router.get("", response_model=List[StreamSchema])
def list_streams():
    state = get_current_state()
    return list(state.stream_states.values())


@router.get("/{stream_id}", response_model=StreamSchema)
def get_stream(stream_id: str):
    state = get_current_state()
    s = state.stream_states.get(stream_id)
    if not s:
        raise HTTPException(status_code=404, detail=f"Stream '{stream_id}' not found")
    return s

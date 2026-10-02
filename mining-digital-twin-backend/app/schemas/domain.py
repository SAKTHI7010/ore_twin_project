"""Shared Pydantic schemas for Plant, Equipment, Stream, Simulation, Alarm, DataQuality, Scenario."""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class EquipmentStatus(str, Enum):
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    WARNING = "WARNING"
    FAULT = "FAULT"
    SIMULATION = "SIMULATION"


class StreamStatus(str, Enum):
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    FAULT = "FAULT"


class AlarmSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class DataMode(str, Enum):
    DEMO = "DEMO"
    SIMULATION = "SIMULATION"
    LIVE = "LIVE"


# ─── Stream ───────────────────────────────────────────────────────────────────

class StreamSchema(BaseModel):
    stream_id: str
    source_id: str
    destination_id: str
    stream_type: str  # e.g. "solids", "water", "slurry", "product"
    timestamp: datetime
    mass_flow_tph: float = Field(description="Mass flow in tonnes per hour")
    water_flow_m3h: float = Field(description="Water flow in m³/h")
    solids_fraction: float = Field(ge=0.0, le=1.0, description="Solids weight fraction 0-1")
    size_mm: Optional[float] = None
    quality: Dict[str, Any] = Field(default_factory=dict)
    status: StreamStatus = StreamStatus.ACTIVE
    mode: DataMode = DataMode.DEMO


# ─── Equipment ────────────────────────────────────────────────────────────────

class EquipmentSchema(BaseModel):
    equipment_id: str
    equipment_type: str
    name: str
    status: EquipmentStatus = EquipmentStatus.SIMULATION
    parameters: Dict[str, Any] = Field(default_factory=dict)
    input_streams: List[str] = Field(default_factory=list)
    output_streams: List[str] = Field(default_factory=list)
    alarms: List[str] = Field(default_factory=list)
    mode: DataMode = DataMode.DEMO


# ─── Plant ────────────────────────────────────────────────────────────────────

class PlantSchema(BaseModel):
    plant_id: str = "ORE-BENEFICIATION-01"
    name: str = "Ore Beneficiation Plant"
    mode: DataMode = DataMode.DEMO
    timestamp: datetime
    overall_status: EquipmentStatus = EquipmentStatus.SIMULATION
    feed_rate_tph: float
    product_rates: Dict[str, float] = Field(default_factory=dict)
    water_usage_m3h: float
    recovery_pct: float
    mass_balance_closure_pct: float
    active_alarms: int = 0


# ─── Alarm ────────────────────────────────────────────────────────────────────

class AlarmSchema(BaseModel):
    alarm_id: str
    equipment_id: Optional[str] = None
    stream_id: Optional[str] = None
    severity: AlarmSeverity
    message: str
    timestamp: datetime
    acknowledged: bool = False


# ─── Mass Balance ─────────────────────────────────────────────────────────────

class MassBalanceSchema(BaseModel):
    timestamp: datetime
    total_feed_tph: float
    product_tph: Dict[str, float]
    reject_tph: float
    tailings_tph: float
    unaccounted_tph: float
    closure_pct: float
    water_in_m3h: float
    water_out_m3h: float
    water_balance_err_pct: float
    warnings: List[str] = Field(default_factory=list)


# ─── Simulation State ─────────────────────────────────────────────────────────

class SimulationInputs(BaseModel):
    feed_rate_tph: float = Field(default=500.0, ge=0)
    feed_moisture_pct: float = Field(default=8.0, ge=0, le=100)
    water_addition_m3h: float = Field(default=200.0, ge=0)
    primary_crusher_css_mm: float = Field(default=150.0, ge=10)
    secondary_crusher_css_mm: float = Field(default=75.0, ge=5)
    scrubber_water_m3h: float = Field(default=80.0, ge=0)
    jig_water_m3h: float = Field(default=50.0, ge=0)
    cyclone_pressure_kpa: float = Field(default=120.0, ge=0)


class SimulationStateSchema(BaseModel):
    scenario_id: str
    timestamp: datetime
    mode: DataMode = DataMode.DEMO
    inputs: SimulationInputs
    equipment_states: Dict[str, EquipmentSchema]
    stream_states: Dict[str, StreamSchema]
    mass_balance: MassBalanceSchema
    validation_warnings: List[str] = Field(default_factory=list)
    is_converged: bool = True


# ─── Scenario ─────────────────────────────────────────────────────────────────

class ScenarioSchema(BaseModel):
    scenario_id: str
    created_at: datetime
    inputs: SimulationInputs
    result_summary: Dict[str, Any] = Field(default_factory=dict)


# ─── Optimization ─────────────────────────────────────────────────────────────

class OptimizationRequest(BaseModel):
    objective: str = "maximize_recovery"
    constraints: Dict[str, Any] = Field(default_factory=dict)


class OptimizationResult(BaseModel):
    objective: str
    recommended_inputs: SimulationInputs
    expected_recovery_pct: float
    expected_throughput_tph: float
    advisory_notes: List[str]
    disclaimer: str = (
        "DEMO ADVISORY ONLY – These recommendations are based on simulated data. "
        "Do NOT use as direct plant control commands without engineering validation."
    )


# ─── Data Quality ─────────────────────────────────────────────────────────────

class DataQualitySchema(BaseModel):
    timestamp: datetime
    source: DataMode
    freshness_seconds: float
    missing_value_count: int
    invalid_range_count: int
    stale_stream_count: int
    mass_balance_ok: bool
    warnings: List[str] = Field(default_factory=list)
    status: str = "OK"


# ─── Overview KPIs ────────────────────────────────────────────────────────────

class PlantOverviewSchema(BaseModel):
    plant: PlantSchema
    equipment_summary: Dict[str, int]  # status -> count
    active_alarms: List[AlarmSchema]
    recent_scenarios: List[ScenarioSchema]
    data_quality: DataQualitySchema

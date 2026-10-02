"""
Deterministic Mock / Demo data generator.
Generates a consistent initial plant state using a fixed random seed.
All frontend views must consume this state via the API — never generate
independent random values in the frontend.
"""
from __future__ import annotations
import random
import uuid
from datetime import datetime, timezone

import numpy as np

from app.schemas.domain import (
    AlarmSchema,
    AlarmSeverity,
    DataMode,
    DataQualitySchema,
    EquipmentSchema,
    EquipmentStatus,
    MassBalanceSchema,
    PlantSchema,
    ScenarioSchema,
    SimulationInputs,
    SimulationStateSchema,
    StreamSchema,
    StreamStatus,
)

SEED = 42
rng = np.random.default_rng(SEED)

# ─── Equipment Catalog ────────────────────────────────────────────────────────

EQUIPMENT_CATALOG: list[dict] = [
    {"equipment_id": "CR-001", "equipment_type": "PrimaryCrusher",    "name": "Primary Jaw Crusher"},
    {"equipment_id": "SC-001", "equipment_type": "VibratingScreen",   "name": "Primary Vibrating Screen"},
    {"equipment_id": "CR-002", "equipment_type": "SecondaryCrusher",  "name": "Secondary Cone Crusher"},
    {"equipment_id": "RS-001", "equipment_type": "RotaryScrubber",    "name": "Rotary Scrubber"},
    {"equipment_id": "JG-001", "equipment_type": "Jig",               "name": "Jig Concentrator 1"},
    {"equipment_id": "SP-001", "equipment_type": "SpiralClassifier",  "name": "Spiral Classifier"},
    {"equipment_id": "HC-001", "equipment_type": "Hydrocyclone",      "name": "Hydrocyclone Cluster"},
    {"equipment_id": "WHIMS-001","equipment_type":"MagneticSeparator","name": "Wet High-Intensity Magnetic Separator"},
    {"equipment_id": "CR-003", "equipment_type": "TertiaryCrusher",   "name": "Tertiary VSI Crusher"},
    {"equipment_id": "SC-002", "equipment_type": "VibratingScreen",   "name": "Tertiary Vibrating Screen"},
    {"equipment_id": "JG-002", "equipment_type": "Jig",               "name": "Jig Concentrator 2"},
    {"equipment_id": "TB-001", "equipment_type": "ShakingTable",      "name": "Shaking Water Table"},
]

# ─── Stream Catalog (source_id → destination_id) ──────────────────────────────

STREAM_CATALOG: list[dict] = [
    # Feed → Primary Crusher
    {"stream_id": "S-001", "source_id": "FEED",    "destination_id": "CR-001", "stream_type": "solids",  "name": "ROM Feed"},
    # CR-001 → SC-001
    {"stream_id": "S-002", "source_id": "CR-001",  "destination_id": "SC-001", "stream_type": "solids",  "name": "Primary Crusher Discharge"},
    # SC-001 → CR-002 (oversize)
    {"stream_id": "S-003", "source_id": "SC-001",  "destination_id": "CR-002", "stream_type": "solids",  "name": "Screen Oversize to Secondary Crusher"},
    # SC-001 → RS-001 (undersize / lump ore route)
    {"stream_id": "S-004", "source_id": "SC-001",  "destination_id": "RS-001", "stream_type": "slurry",  "name": "Screen Undersize / Ore Lumps"},
    # CR-002 → RS-001
    {"stream_id": "S-005", "source_id": "CR-002",  "destination_id": "RS-001", "stream_type": "solids",  "name": "Secondary Crusher Discharge"},
    # Water → RS-001
    {"stream_id": "S-006", "source_id": "WATER",   "destination_id": "RS-001", "stream_type": "water",   "name": "Scrubber Water Addition"},
    # RS-001 → JG-001
    {"stream_id": "S-007", "source_id": "RS-001",  "destination_id": "JG-001", "stream_type": "slurry",  "name": "Scrubber Discharge to Jig"},
    # JG-001 concentrate → PRODUCT
    {"stream_id": "S-008", "source_id": "JG-001",  "destination_id": "SP-001", "stream_type": "slurry",  "name": "Jig1 Concentrate to Spiral"},
    # JG-001 tailings
    {"stream_id": "S-009", "source_id": "JG-001",  "destination_id": "TAILS", "stream_type": "slurry",   "name": "Jig1 Tailings"},
    # SP-001 → HC-001
    {"stream_id": "S-010", "source_id": "SP-001",  "destination_id": "HC-001", "stream_type": "slurry",  "name": "Spiral Classifier Overflow"},
    # HC-001 underflow → WHIMS-001
    {"stream_id": "S-011", "source_id": "HC-001",  "destination_id": "WHIMS-001","stream_type":"slurry", "name": "Cyclone Underflow to WHIMS"},
    # HC-001 overflow → TAILS
    {"stream_id": "S-012", "source_id": "HC-001",  "destination_id": "TAILS", "stream_type": "slurry",   "name": "Cyclone Overflow (fines) to Tailings"},
    # WHIMS-001 concentrate (pellets) → PRODUCT
    {"stream_id": "S-013", "source_id": "WHIMS-001","destination_id":"PELLET","stream_type": "product",   "name": "WHIMS Pellet Concentrate"},
    # WHIMS-001 middlings → CR-003
    {"stream_id": "S-014", "source_id": "WHIMS-001","destination_id":"CR-003","stream_type": "slurry",    "name": "WHIMS Middlings to Tertiary Crusher"},
    # WHIMS-001 tailings
    {"stream_id": "S-015", "source_id": "WHIMS-001","destination_id":"TAILS", "stream_type": "slurry",    "name": "WHIMS Tailings"},
    # CR-003 → SC-002
    {"stream_id": "S-016", "source_id": "CR-003",  "destination_id": "SC-002", "stream_type": "slurry",  "name": "Tertiary Crusher Discharge"},
    # SC-002 → JG-002
    {"stream_id": "S-017", "source_id": "SC-002",  "destination_id": "JG-002", "stream_type": "slurry",  "name": "Tertiary Screen Undersize to Jig2"},
    # JG-002 → TB-001
    {"stream_id": "S-018", "source_id": "JG-002",  "destination_id": "TB-001", "stream_type": "slurry",  "name": "Jig2 Concentrate to Shaking Table"},
    # JG-002 tailings
    {"stream_id": "S-019", "source_id": "JG-002",  "destination_id": "TAILS", "stream_type": "slurry",   "name": "Jig2 Tailings"},
    # TB-001 → Ore Fines product
    {"stream_id": "S-020", "source_id": "TB-001",  "destination_id": "ORE_FINES","stream_type":"product", "name": "Shaking Table Ore Fines Concentrate"},
    # TB-001 → Middlings
    {"stream_id": "S-021", "source_id": "TB-001",  "destination_id": "MIDDLINGS","stream_type":"product", "name": "Shaking Table Middlings"},
    # TB-001 tailings
    {"stream_id": "S-022", "source_id": "TB-001",  "destination_id": "TAILS", "stream_type": "slurry",   "name": "Shaking Table Reject/Tailings"},
    # Lump Ore product from SC-001 coarse route
    {"stream_id": "S-023", "source_id": "SC-001",  "destination_id": "LUMP_ORE","stream_type":"product",  "name": "Lump Ore Product"},
]


def _noise(base: float, pct: float = 0.03) -> float:
    """Add small deterministic noise."""
    return float(base * (1 + rng.uniform(-pct, pct)))


def build_equipment_states(status: EquipmentStatus = EquipmentStatus.SIMULATION) -> dict[str, EquipmentSchema]:
    eq_map: dict[str, EquipmentSchema] = {}
    stream_inputs: dict[str, list[str]] = {}
    stream_outputs: dict[str, list[str]] = {}

    for s in STREAM_CATALOG:
        stream_outputs.setdefault(s["source_id"], []).append(s["stream_id"])
        stream_inputs.setdefault(s["destination_id"], []).append(s["stream_id"])

    for cat in EQUIPMENT_CATALOG:
        eid = cat["equipment_id"]
        etype = cat["equipment_type"]
        params: dict = {}

        if etype == "PrimaryCrusher":
            params = {"css_mm": 150, "power_kw": _noise(1200), "throughput_tph": _noise(500)}
        elif etype == "VibratingScreen":
            params = {"aperture_mm": 10 if eid == "SC-001" else 3, "efficiency_pct": _noise(92)}
        elif etype == "SecondaryCrusher":
            params = {"css_mm": 75, "power_kw": _noise(800), "throughput_tph": _noise(280)}
        elif etype == "RotaryScrubber":
            params = {"drum_speed_rpm": _noise(14), "water_addition_m3h": _noise(80), "retention_time_min": _noise(8)}
        elif etype == "Jig":
            params = {"stroke_mm": _noise(25), "frequency_spm": _noise(120), "water_m3h": _noise(50)}
        elif etype == "SpiralClassifier":
            params = {"pitch_mm": _noise(280), "speed_rpm": _noise(2.5)}
        elif etype == "Hydrocyclone":
            params = {"inlet_pressure_kpa": _noise(120), "vortex_finder_mm": _noise(35), "spigot_mm": _noise(12)}
        elif etype == "MagneticSeparator":
            params = {"field_intensity_kA_m": _noise(800), "matrix_type": "steel_wool", "throughput_tph": _noise(80)}
        elif etype == "TertiaryCrusher":
            params = {"tip_speed_m_s": _noise(55), "power_kw": _noise(400)}
        elif etype == "ShakingTable":
            params = {"stroke_mm": _noise(18), "frequency_spm": _noise(300), "water_m3h": _noise(12)}

        eq_map[eid] = EquipmentSchema(
            equipment_id=eid,
            equipment_type=etype,
            name=cat["name"],
            status=status,
            parameters=params,
            input_streams=stream_inputs.get(eid, []),
            output_streams=stream_outputs.get(eid, []),
            mode=DataMode.DEMO,
        )
    return eq_map


def build_stream_states(feed_tph: float = 500.0) -> dict[str, StreamSchema]:
    now = datetime.now(timezone.utc)
    streams: dict[str, StreamSchema] = {}

    # Simple mass-split factors (configurable; not validated plant values)
    splits = {
        "S-001": (feed_tph, 0.0, 0.82),
        "S-002": (feed_tph * 0.98, 0.0, 0.82),
        "S-003": (feed_tph * 0.40, 0.0, 0.82),
        "S-004": (feed_tph * 0.55, 5.0, 0.70),
        "S-005": (feed_tph * 0.38, 0.0, 0.82),
        "S-006": (0.0, 80.0, 0.0),
        "S-007": (feed_tph * 0.92, 80.0, 0.55),
        "S-008": (feed_tph * 0.60, 30.0, 0.65),
        "S-009": (feed_tph * 0.30, 50.0, 0.40),
        "S-010": (feed_tph * 0.55, 30.0, 0.40),
        "S-011": (feed_tph * 0.30, 15.0, 0.55),
        "S-012": (feed_tph * 0.20, 15.0, 0.25),
        "S-013": (feed_tph * 0.18, 5.0, 0.70),
        "S-014": (feed_tph * 0.08, 8.0, 0.60),
        "S-015": (feed_tph * 0.04, 2.0, 0.30),
        "S-016": (feed_tph * 0.07, 8.0, 0.60),
        "S-017": (feed_tph * 0.06, 5.0, 0.55),
        "S-018": (feed_tph * 0.035, 3.0, 0.65),
        "S-019": (feed_tph * 0.025, 2.0, 0.35),
        "S-020": (feed_tph * 0.020, 1.5, 0.70),
        "S-021": (feed_tph * 0.010, 1.0, 0.50),
        "S-022": (feed_tph * 0.005, 0.5, 0.25),
        "S-023": (feed_tph * 0.025, 2.0, 0.85),
    }

    for cat in STREAM_CATALOG:
        sid = cat["stream_id"]
        mf, wf, sf = splits.get(sid, (0.0, 0.0, 0.5))
        streams[sid] = StreamSchema(
            stream_id=sid,
            source_id=cat["source_id"],
            destination_id=cat["destination_id"],
            stream_type=cat["stream_type"],
            timestamp=now,
            mass_flow_tph=_noise(mf),
            water_flow_m3h=_noise(wf) if wf > 0 else 0.0,
            solids_fraction=min(1.0, max(0.0, _noise(sf, 0.02))),
            status=StreamStatus.ACTIVE,
            mode=DataMode.DEMO,
        )
    return streams


def build_mass_balance(streams: dict[str, StreamSchema]) -> MassBalanceSchema:
    now = datetime.now(timezone.utc)
    feed = streams["S-001"].mass_flow_tph
    products = {
        "pellet": streams["S-013"].mass_flow_tph,
        "lump_ore": streams["S-023"].mass_flow_tph,
        "ore_fines": streams["S-020"].mass_flow_tph,
        "middlings": streams["S-021"].mass_flow_tph,
    }
    tailings = (
        streams["S-009"].mass_flow_tph
        + streams["S-012"].mass_flow_tph
        + streams["S-015"].mass_flow_tph
        + streams["S-019"].mass_flow_tph
        + streams["S-022"].mass_flow_tph
    )
    product_total = sum(products.values())
    accounted = product_total + tailings
    unaccounted = feed - accounted
    closure = (accounted / feed * 100) if feed > 0 else 0.0

    water_in = sum(
        s.water_flow_m3h for s in streams.values()
        if s.source_id in ("WATER",)
    ) + streams["S-001"].water_flow_m3h
    water_out = sum(
        s.water_flow_m3h for s in streams.values()
        if s.destination_id in ("TAILS", "PELLET", "ORE_FINES", "MIDDLINGS", "LUMP_ORE")
    )
    water_err = abs(water_in - water_out) / (water_in + 1e-6) * 100

    warnings = []
    if abs(closure - 100) > 5:
        warnings.append(f"Mass balance closure {closure:.1f}% is outside ±5% — check flow splits.")
    if water_err > 10:
        warnings.append(f"Water balance error {water_err:.1f}% — check water addition/removal streams.")

    return MassBalanceSchema(
        timestamp=now,
        total_feed_tph=feed,
        product_tph=products,
        reject_tph=0.0,
        tailings_tph=tailings,
        unaccounted_tph=unaccounted,
        closure_pct=closure,
        water_in_m3h=water_in,
        water_out_m3h=water_out,
        water_balance_err_pct=water_err,
        warnings=warnings,
    )


def build_alarms() -> list[AlarmSchema]:
    now = datetime.now(timezone.utc)
    return [
        AlarmSchema(
            alarm_id="ALM-001",
            equipment_id="HC-001",
            severity=AlarmSeverity.WARNING,
            message="Cyclone inlet pressure slightly elevated — check pump speed. [DEMO]",
            timestamp=now,
            acknowledged=False,
        ),
        AlarmSchema(
            alarm_id="ALM-002",
            equipment_id="WHIMS-001",
            severity=AlarmSeverity.INFO,
            message="WHIMS matrix flushing cycle scheduled in 2 h. [DEMO]",
            timestamp=now,
            acknowledged=True,
        ),
    ]


def build_data_quality(streams: dict[str, StreamSchema]) -> DataQualitySchema:
    now = datetime.now(timezone.utc)
    return DataQualitySchema(
        timestamp=now,
        source=DataMode.DEMO,
        freshness_seconds=0.0,
        missing_value_count=0,
        invalid_range_count=0,
        stale_stream_count=0,
        mass_balance_ok=True,
        warnings=["All values are DEMO/SIMULATION data. Not validated plant operating data."],
        status="OK",
    )


def build_simulation_state(inputs: SimulationInputs | None = None) -> SimulationStateSchema:
    if inputs is None:
        inputs = SimulationInputs()
    now = datetime.now(timezone.utc)
    scenario_id = f"SCN-{now.strftime('%Y%m%dT%H%M%S')}-DEMO"
    eq_states = build_equipment_states()
    stream_states = build_stream_states(inputs.feed_rate_tph)
    mass_bal = build_mass_balance(stream_states)

    return SimulationStateSchema(
        scenario_id=scenario_id,
        timestamp=now,
        mode=DataMode.DEMO,
        inputs=inputs,
        equipment_states=eq_states,
        stream_states=stream_states,
        mass_balance=mass_bal,
        validation_warnings=mass_bal.warnings,
        is_converged=True,
    )


# ─── Singleton state store ─────────────────────────────────────────────────────

_current_state: SimulationStateSchema | None = None
_scenarios: list[ScenarioSchema] = []


def get_current_state() -> SimulationStateSchema:
    global _current_state
    if _current_state is None:
        _current_state = build_simulation_state()
    return _current_state


def run_simulation(inputs: SimulationInputs) -> SimulationStateSchema:
    global _current_state, _scenarios
    _current_state = build_simulation_state(inputs)
    _scenarios.append(
        ScenarioSchema(
            scenario_id=_current_state.scenario_id,
            created_at=_current_state.timestamp,
            inputs=inputs,
            result_summary={
                "feed_tph": inputs.feed_rate_tph,
                "closure_pct": _current_state.mass_balance.closure_pct,
            },
        )
    )
    return _current_state


def get_scenarios() -> list[ScenarioSchema]:
    return list(reversed(_scenarios[-20:]))

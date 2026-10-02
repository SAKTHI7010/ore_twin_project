"""Basic backend tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "OK"


def test_plant_overview():
    r = client.get("/api/v1/plant/overview")
    assert r.status_code == 200
    data = r.json()
    assert "plant" in data
    assert data["plant"]["feed_rate_tph"] > 0


def test_equipment_list():
    r = client.get("/api/v1/equipment")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 10
    ids = {e["equipment_id"] for e in items}
    assert "CR-001" in ids
    assert "WHIMS-001" in ids


def test_equipment_detail():
    r = client.get("/api/v1/equipment/CR-001")
    assert r.status_code == 200
    assert r.json()["equipment_id"] == "CR-001"


def test_equipment_not_found():
    r = client.get("/api/v1/equipment/INVALID-999")
    assert r.status_code == 404


def test_streams_list():
    r = client.get("/api/v1/streams")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 20


def test_stream_detail():
    r = client.get("/api/v1/streams/S-001")
    assert r.status_code == 200
    assert r.json()["stream_id"] == "S-001"


def test_simulation_state():
    r = client.get("/api/v1/simulation/state")
    assert r.status_code == 200
    data = r.json()
    assert "mass_balance" in data
    assert data["mass_balance"]["closure_pct"] > 0


def test_simulation_run():
    payload = {
        "feed_rate_tph": 450.0,
        "feed_moisture_pct": 7.0,
        "water_addition_m3h": 190.0,
        "primary_crusher_css_mm": 140.0,
        "secondary_crusher_css_mm": 70.0,
        "scrubber_water_m3h": 85.0,
        "jig_water_m3h": 55.0,
        "cyclone_pressure_kpa": 125.0,
    }
    r = client.post("/api/v1/simulation/run", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["inputs"]["feed_rate_tph"] == 450.0


def test_mass_balance():
    r = client.get("/api/v1/analytics/mass-balance")
    assert r.status_code == 200
    mb = r.json()
    assert "closure_pct" in mb
    assert mb["total_feed_tph"] > 0


def test_trends():
    r = client.get("/api/v1/analytics/trends")
    assert r.status_code == 200
    d = r.json()
    assert "feed_rate_tph" in d


def test_optimization():
    r = client.post("/api/v1/optimization/run", json={"objective": "maximize_recovery"})
    assert r.status_code == 200
    d = r.json()
    assert "disclaimer" in d


def test_data_quality():
    r = client.get("/api/v1/data-quality")
    assert r.status_code == 200
    assert r.json()["status"] == "OK"

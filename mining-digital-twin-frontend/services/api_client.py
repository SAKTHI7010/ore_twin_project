"""
API Client for the Ore Beneficiation Digital Twin backend.
All frontend data must come through this client — never independently generate values.
"""
import os
import requests
import streamlit as st
from typing import Any, Dict, Optional

# ─── Backend URL Resolution ───────────────────────────────────────────────────

def _get_backend_url() -> str:
    # 1. Streamlit secrets (Streamlit Cloud deployment)
    try:
        return st.secrets["BACKEND_BASE_URL"].rstrip("/")
    except Exception:
        pass
    # 2. Environment variable (local dev / Render)
    url = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000").rstrip("/")
    return url


BACKEND_BASE_URL = _get_backend_url()


# ─── HTTP helpers ─────────────────────────────────────────────────────────────

def _get(path: str, params: Optional[Dict] = None) -> Any:
    url = f"{BACKEND_BASE_URL}{path}"
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(
            f"⚠️ Cannot connect to backend at **{BACKEND_BASE_URL}**. "
            "Ensure the backend is running or set `BACKEND_BASE_URL` correctly."
        )
        return None
    except requests.exceptions.Timeout:
        st.warning("⏳ Backend request timed out. Render free tier may be cold-starting — please retry.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend HTTP error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def _post(path: str, payload: Dict) -> Any:
    url = f"{BACKEND_BASE_URL}{path}"
    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(f"⚠️ Cannot connect to backend at **{BACKEND_BASE_URL}**.")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ─── API Methods ──────────────────────────────────────────────────────────────

def get_health() -> Optional[Dict]:
    return _get("/health")


def get_plant_overview() -> Optional[Dict]:
    return _get("/api/v1/plant/overview")


def get_equipment_list() -> Optional[list]:
    return _get("/api/v1/equipment")


def get_equipment_detail(equipment_id: str) -> Optional[Dict]:
    return _get(f"/api/v1/equipment/{equipment_id}")


def get_streams_list() -> Optional[list]:
    return _get("/api/v1/streams")


def get_stream_detail(stream_id: str) -> Optional[Dict]:
    return _get(f"/api/v1/streams/{stream_id}")


def get_simulation_state() -> Optional[Dict]:
    return _get("/api/v1/simulation/state")


def run_simulation(inputs: Dict) -> Optional[Dict]:
    return _post("/api/v1/simulation/run", inputs)


def get_mass_balance() -> Optional[Dict]:
    return _get("/api/v1/analytics/mass-balance")


def get_trends() -> Optional[Dict]:
    return _get("/api/v1/analytics/trends")


def run_optimization(objective: str = "maximize_recovery", constraints: Dict = {}) -> Optional[Dict]:
    return _post("/api/v1/optimization/run", {"objective": objective, "constraints": constraints})


def get_data_quality() -> Optional[Dict]:
    return _get("/api/v1/data-quality")

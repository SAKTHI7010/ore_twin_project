"""Page: Simulation"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import plotly.graph_objects as go

from services.api_client import get_simulation_state, run_simulation
from components.ui_helpers import demo_warning

st.set_page_config(page_title="Simulation", page_icon="🔬", layout="wide")
st.title("🔬 Simulation Control")
demo_warning()
st.markdown(
    "> **Note:** This is a deterministic, configurable process simulation. "
    "Results are reproducible DEMO data and do not represent validated plant parameters."
)

# ─── Load current state ───────────────────────────────────────────────────────
state = get_simulation_state()
if not state:
    st.error("Cannot load simulation state.")
    st.stop()

current_inputs = state.get("inputs", {})

# ─── Input controls ───────────────────────────────────────────────────────────
st.markdown("### ⚙️ Simulation Inputs")
with st.form("sim_form"):
    c1, c2 = st.columns(2)
    with c1:
        feed_rate = st.slider("Feed Rate (t/h)", 100, 1000, int(current_inputs.get("feed_rate_tph", 500)), 10)
        feed_moisture = st.slider("Feed Moisture (%)", 0, 30, int(current_inputs.get("feed_moisture_pct", 8)), 1)
        water_add = st.slider("Water Addition (m³/h)", 50, 500, int(current_inputs.get("water_addition_m3h", 200)), 10)
        primary_css = st.slider("Primary Crusher CSS (mm)", 80, 250, int(current_inputs.get("primary_crusher_css_mm", 150)), 5)
    with c2:
        secondary_css = st.slider("Secondary Crusher CSS (mm)", 30, 120, int(current_inputs.get("secondary_crusher_css_mm", 75)), 5)
        scrubber_water = st.slider("Scrubber Water (m³/h)", 20, 200, int(current_inputs.get("scrubber_water_m3h", 80)), 5)
        jig_water = st.slider("Jig Water (m³/h)", 10, 150, int(current_inputs.get("jig_water_m3h", 50)), 5)
        cyclone_p = st.slider("Cyclone Pressure (kPa)", 60, 200, int(current_inputs.get("cyclone_pressure_kpa", 120)), 5)

    run = st.form_submit_button("▶ Run Simulation Step", type="primary", use_container_width=True)

# ─── Run simulation ───────────────────────────────────────────────────────────
if run:
    payload = {
        "feed_rate_tph": float(feed_rate),
        "feed_moisture_pct": float(feed_moisture),
        "water_addition_m3h": float(water_add),
        "primary_crusher_css_mm": float(primary_css),
        "secondary_crusher_css_mm": float(secondary_css),
        "scrubber_water_m3h": float(scrubber_water),
        "jig_water_m3h": float(jig_water),
        "cyclone_pressure_kpa": float(cyclone_p),
    }
    with st.spinner("Running simulation..."):
        result = run_simulation(payload)
    if result:
        state = result
        st.success(f"✅ Simulation complete — Scenario ID: `{result['scenario_id']}`")

# ─── Results ──────────────────────────────────────────────────────────────────
mb = state.get("mass_balance", {})
if mb:
    st.markdown("### 📊 Simulation Results — Mass Balance")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Feed", f"{mb.get('total_feed_tph',0):.1f} t/h")
    r2.metric("Products", f"{sum(mb.get('product_tph',{}).values()):.1f} t/h")
    r3.metric("Tailings", f"{mb.get('tailings_tph',0):.1f} t/h")
    r4.metric("Closure", f"{mb.get('closure_pct',0):.1f}%",
              delta=f"{mb.get('closure_pct',0)-100:.1f}%")

    # Sankey-style chart
    products = mb.get("product_tph", {})
    feed = mb.get("total_feed_tph", 1)
    labels = ["Feed"] + [k.replace("_"," ").title() for k in products] + ["Tailings","Unaccounted"]
    sources = [0] * (len(products) + 2)
    targets = list(range(1, len(products) + 3))
    values = list(products.values()) + [mb.get("tailings_tph", 0), max(0, mb.get("unaccounted_tph", 0))]

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=20,
            label=labels,
            color=["#F97316","#A78BFA","#22C55E","#34D399","#FBBF24","#94A3B8","#475569"],
        ),
        link=dict(source=sources, target=targets, value=values,
                  color=["rgba(249,115,22,0.3)"]*len(values)),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#F1F5F9"), height=350,
        margin=dict(t=20, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    if state.get("validation_warnings"):
        st.warning("⚠️ Validation Warnings")
        for w in state["validation_warnings"]:
            st.caption(f"• {w}")

    st.caption(f"Scenario: `{state.get('scenario_id')}` | Timestamp: {state.get('timestamp')}")

"""
Ore Beneficiation Digital Twin — Streamlit Frontend
Main entry point (Home / Plant Overview)
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from services.api_client import get_plant_overview, get_health, BACKEND_BASE_URL
from components.ui_helpers import demo_warning, metric_card, STATUS_COLOR, PRODUCT_COLORS

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ore Beneficiation Digital Twin",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
    border: 1px solid #F97316;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(249,115,22,0.08) 0%, transparent 60%);
    animation: pulse 4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
.main-header h1 { color: #F97316; font-size: 1.9em; font-weight: 700; margin: 0; }
.main-header p { color: #94A3B8; font-size: 0.95em; margin: 4px 0 0; }
.section-title { 
    color: #F97316; font-size: 1.1em; font-weight: 600; 
    border-bottom: 1px solid #334155; padding-bottom: 6px; margin: 20px 0 12px;
}
.flowsheet-node {
    background: #1E293B; border: 2px solid #334155; border-radius: 8px;
    padding: 10px 14px; text-align: center; font-size: 11px; color: #CBD5E1;
    transition: all 0.2s;
}
.alert-card {
    background: #1E293B; border-left: 3px solid #F59E0B;
    border-radius: 6px; padding: 10px 14px; margin: 6px 0; font-size: 0.85em;
}
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>⛏️ Ore Beneficiation Digital Twin</h1>
  <p>Real-time simulation monitoring for ore processing operations &nbsp;|&nbsp; 
  <span style="color:#F97316">Backend:</span> <code style="color:#38BDF8">""" + BACKEND_BASE_URL + """</code></p>
</div>
""", unsafe_allow_html=True)

demo_warning()

# ─── Backend health status ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ System")
    health = get_health()
    if health:
        st.success(f"✅ Backend Online — v{health.get('version','?')}")
    else:
        st.error("❌ Backend Offline")
    st.markdown(f"**Backend URL:** `{BACKEND_BASE_URL}`")
    st.markdown("---")
    st.markdown("### Navigation")
    st.info("Use the **Pages** menu above to navigate between screens.")

# ─── Load data ────────────────────────────────────────────────────────────────
with st.spinner("Loading plant state..."):
    overview = get_plant_overview()

if not overview:
    st.error("Could not load plant overview. Check backend connection.")
    st.stop()

plant = overview["plant"]
alarms = overview.get("active_alarms", [])
dq = overview.get("data_quality", {})

# ─── KPI Row ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Plant Key Performance Indicators</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1: metric_card("Feed Rate", f"{plant['feed_rate_tph']:.1f} t/h", "ROM Ore Input", "#F97316")
with c2: metric_card("Recovery", f"{plant['recovery_pct']:.1f}%", "Product / Feed", "#22C55E")
with c3: metric_card("Mass Balance", f"{plant['mass_balance_closure_pct']:.1f}%", "Closure %", "#38BDF8")
with c4: metric_card("Water Usage", f"{plant['water_usage_m3h']:.0f} m³/h", "Process Water", "#A78BFA")
with c5: metric_card("Active Alarms", str(plant.get("active_alarms", 0)), "Unacknowledged", "#F59E0B" if plant.get("active_alarms",0)>0 else "#22C55E")

# ─── Product Distribution Chart ───────────────────────────────────────────────
col_chart, col_alarms = st.columns([2, 1])

with col_chart:
    st.markdown('<div class="section-title">🏭 Product Distribution</div>', unsafe_allow_html=True)
    products = plant.get("product_rates", {})
    if products:
        labels = [k.replace("_", " ").title() for k in products]
        values = list(products.values())
        colors = [PRODUCT_COLORS.get(k, "#94A3B8") for k in products]
        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            marker=dict(colors=colors, line=dict(color="#0F172A", width=2)),
            hole=0.52,
            textinfo="label+percent",
            textfont=dict(size=12, color="#F1F5F9"),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F1F5F9"),
            margin=dict(t=20, b=10, l=20, r=20),
            showlegend=True,
            legend=dict(font=dict(color="#94A3B8")),
            annotations=[dict(
                text=f"<b>{sum(values):.1f}</b><br>t/h total",
                x=0.5, y=0.5, font_size=14, showarrow=False,
                font=dict(color="#F1F5F9"),
            )]
        )
        st.plotly_chart(fig, use_container_width=True)

with col_alarms:
    st.markdown('<div class="section-title">🚨 Active Alarms</div>', unsafe_allow_html=True)
    if alarms:
        for a in alarms:
            col = "#F59E0B" if a["severity"] == "WARNING" else "#EF4444" if a["severity"] == "CRITICAL" else "#38BDF8"
            ack = "✅" if a.get("acknowledged") else "🔔"
            st.markdown(
                f'<div class="alert-card" style="border-color:{col}">'
                f'<b style="color:{col}">{ack} {a["severity"]}</b> — {a.get("equipment_id","")}<br>'
                f'<span style="color:#CBD5E1">{a["message"]}</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.success("✅ No active alarms")

# ─── 2D Process Flowsheet (Plotly) ────────────────────────────────────────────
st.markdown('<div class="section-title">🗺️ Interactive Process Flowsheet</div>', unsafe_allow_html=True)
st.caption("⚠️ DEMO schematic — values from backend simulation state")

# Equipment positions for flowsheet
eq_pos = {
    "CR-001": (1, 8), "SC-001": (3, 8), "CR-002": (3, 6),
    "RS-001": (5, 7), "JG-001": (7, 7), "SP-001": (9, 8),
    "HC-001": (11, 8), "WHIMS-001": (13, 7), "CR-003": (13, 5),
    "SC-002": (11, 4), "JG-002": (9, 4), "TB-001": (7, 4),
}
eq_labels = {
    "CR-001":"Primary\nCrusher", "SC-001":"Screen 1", "CR-002":"Secondary\nCrusher",
    "RS-001":"Rotary\nScrubber", "JG-001":"Jig 1", "SP-001":"Spiral\nClassifier",
    "HC-001":"Hydro-\ncyclone", "WHIMS-001":"WHIMS", "CR-003":"Tertiary\nCrusher",
    "SC-002":"Screen 2", "JG-002":"Jig 2", "TB-001":"Shaking\nTable",
}
edges = [
    ("CR-001","SC-001"),("SC-001","CR-002"),("SC-001","RS-001"),
    ("CR-002","RS-001"),("RS-001","JG-001"),("JG-001","SP-001"),
    ("SP-001","HC-001"),("HC-001","WHIMS-001"),("WHIMS-001","CR-003"),
    ("CR-003","SC-002"),("SC-002","JG-002"),("JG-002","TB-001"),
]

fig2 = go.Figure()
for s, d in edges:
    x0,y0 = eq_pos[s]; x1,y1 = eq_pos[d]
    fig2.add_trace(go.Scatter(
        x=[x0,x1,None], y=[y0,y1,None],
        mode='lines',
        line=dict(color='#F97316', width=2.5),
        showlegend=False, hoverinfo='skip',
    ))

for eid, (x,y) in eq_pos.items():
    fig2.add_trace(go.Scatter(
        x=[x], y=[y], mode='markers+text',
        marker=dict(size=28, color='#1E293B', line=dict(color='#38BDF8', width=2), symbol='square'),
        text=[eq_labels.get(eid,eid)], textposition='top center',
        textfont=dict(size=9, color='#CBD5E1'),
        name=eid,
        customdata=[eid],
        hovertemplate=f"<b>{eid}</b><br>{eq_labels.get(eid,'')}<extra></extra>",
    ))

# Products
for label, pos in [("ROM\nFeed",(-.5,8)),("Pellet\nProduct",(15,7)),("Lump\nOre",(5,9.5)),("Ore\nFines",(5,2.5)),("Tailings",(7,2))]:
    fig2.add_trace(go.Scatter(
        x=[pos[0]],y=[pos[1]],mode='markers+text',
        marker=dict(size=18,color='#0F172A',line=dict(color='#F97316',width=2),symbol='diamond'),
        text=[label],textposition='top center',
        textfont=dict(size=8,color='#F97316'),
        showlegend=False,hoverinfo='skip',
    ))

fig2.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,1)',
    height=340, margin=dict(t=20,b=20,l=10,r=10),
    xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
    yaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
    showlegend=False,
)
selected = st.plotly_chart(fig2, use_container_width=True, on_select="rerun", selection_mode="points", key="flowsheet")

# Show equipment detail on click
if selected and selected.get("selection") and selected["selection"].get("points"):
    pt = selected["selection"]["points"][0]
    eid = pt.get("customdata") or pt.get("trace_name","")
    if eid and eid in eq_labels:
        st.info(f"ℹ️ Selected: **{eid}** — Navigate to **Equipment Details** page for full data.")

# ─── Data Quality Summary ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">📡 Data Quality</div>', unsafe_allow_html=True)
dq_col1, dq_col2, dq_col3, dq_col4 = st.columns(4)
with dq_col1: st.metric("Source Mode", dq.get("source","DEMO"))
with dq_col2: st.metric("Missing Values", dq.get("missing_value_count", 0))
with dq_col3: st.metric("Invalid Ranges", dq.get("invalid_range_count", 0))
with dq_col4: st.metric("Mass Balance", "✅ OK" if dq.get("mass_balance_ok") else "❌ Error")
if dq.get("warnings"):
    for w in dq["warnings"]:
        st.caption(f"⚠️ {w}")

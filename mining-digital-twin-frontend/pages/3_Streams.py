"""Page: Streams"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import plotly.express as px
import pandas as pd

from services.api_client import get_streams_list, get_stream_detail
from components.ui_helpers import demo_warning

st.set_page_config(page_title="Process Streams", page_icon="🌊", layout="wide")
st.title("🌊 Process Streams")
demo_warning()

streams = get_streams_list()
if not streams:
    st.error("Cannot load streams.")
    st.stop()

# ─── Overview table ───────────────────────────────────────────────────────────
df = pd.DataFrame([{
    "Stream ID": s["stream_id"],
    "Source": s["source_id"],
    "Destination": s["destination_id"],
    "Type": s["stream_type"],
    "Mass Flow (t/h)": round(s["mass_flow_tph"], 2),
    "Water Flow (m³/h)": round(s["water_flow_m3h"], 2),
    "Solids %": f"{s['solids_fraction']*100:.1f}%",
    "Status": s["status"],
} for s in streams])

# Color-coded mass flow bar chart
st.markdown("#### Mass Flow by Stream")
fig = px.bar(
    df, x="Stream ID", y="Mass Flow (t/h)", color="Type",
    color_discrete_sequence=["#F97316","#38BDF8","#22C55E","#A78BFA"],
)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,1)",
    font=dict(color="#F1F5F9"), height=300,
    margin=dict(t=20, b=40, l=20, r=20),
    legend=dict(font=dict(color="#94A3B8")),
    xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
    yaxis=dict(gridcolor="#1E293B"),
)
st.plotly_chart(fig, use_container_width=True)

# ─── Streams table ────────────────────────────────────────────────────────────
st.markdown("#### Stream Data Table")
st.dataframe(df, use_container_width=True, hide_index=True)

# ─── Stream detail ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Inspect Stream")
stream_ids = [s["stream_id"] for s in streams]
sel = st.selectbox("Select Stream", stream_ids)
detail = get_stream_detail(sel)
if detail:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Mass Flow", f"{detail['mass_flow_tph']:.2f} t/h")
        st.metric("Source", detail['source_id'])
    with c2:
        st.metric("Water Flow", f"{detail['water_flow_m3h']:.2f} m³/h")
        st.metric("Destination", detail['destination_id'])
    with c3:
        st.metric("Solids Fraction", f"{detail['solids_fraction']*100:.1f}%")
        st.metric("Stream Type", detail['stream_type'])
    st.caption(f"Timestamp: {detail['timestamp']} | Mode: {detail.get('mode','DEMO')}")

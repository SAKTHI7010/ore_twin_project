"""Page: Data Quality"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import plotly.graph_objects as go

from services.api_client import get_data_quality, get_streams_list
from components.ui_helpers import demo_warning

st.set_page_config(page_title="Data Quality", page_icon="📡", layout="wide")
st.title("📡 Data Quality Monitor")
demo_warning()

dq = get_data_quality()
if not dq:
    st.error("Cannot load data quality info.")
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Source Mode", dq.get("source","DEMO"))
c2.metric("Missing Values", dq.get("missing_value_count",0))
c3.metric("Invalid Ranges", dq.get("invalid_range_count",0))
c4.metric("Stale Streams", dq.get("stale_stream_count",0))
c5.metric("Mass Balance", "✅ OK" if dq.get("mass_balance_ok") else "❌ Error")

st.markdown("---")

# Status gauge
status = dq.get("status","OK")
status_color = "#22C55E" if status == "OK" else "#F59E0B"

fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=100 - dq.get("missing_value_count",0) - dq.get("invalid_range_count",0)*2,
    title={"text": "Data Quality Score", "font": {"color": "#F1F5F9"}},
    delta={"reference": 100, "increasing": {"color": "#22C55E"}, "decreasing": {"color": "#EF4444"}},
    gauge={
        "axis": {"range": [0, 100], "tickcolor": "#94A3B8"},
        "bar": {"color": status_color},
        "bgcolor": "#1E293B",
        "bordercolor": "#334155",
        "steps": [
            {"range": [0, 60], "color": "#450a0a"},
            {"range": [60, 80], "color": "#451a00"},
            {"range": [80, 100], "color": "#052e16"},
        ],
        "threshold": {"line": {"color": "#F97316", "width": 4}, "thickness": 0.75, "value": 95},
    },
))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#F1F5F9"),
    height=280, margin=dict(t=20, b=0, l=20, r=20),
)
st.plotly_chart(fig, use_container_width=True)

if dq.get("warnings"):
    st.markdown("#### ⚠️ Data Quality Warnings")
    for w in dq["warnings"]:
        st.warning(w)

# Stream freshness table
st.markdown("#### 🌊 Stream Freshness")
streams = get_streams_list()
if streams:
    import pandas as pd
    df = pd.DataFrame([{
        "Stream ID": s["stream_id"],
        "Source": s["source_id"],
        "Destination": s["destination_id"],
        "Mass Flow (t/h)": round(s["mass_flow_tph"],2),
        "Status": s["status"],
        "Mode": s.get("mode","DEMO"),
        "Timestamp": s["timestamp"],
    } for s in streams])
    st.dataframe(df, use_container_width=True, hide_index=True)

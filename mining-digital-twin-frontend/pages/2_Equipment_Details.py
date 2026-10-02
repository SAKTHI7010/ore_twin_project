"""Page: Equipment Details"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import plotly.graph_objects as go
import json

from services.api_client import get_equipment_list, get_equipment_detail
from components.ui_helpers import demo_warning, STATUS_COLOR

st.set_page_config(page_title="Equipment Details", page_icon="⚙️", layout="wide")
st.title("⚙️ Equipment Details")
demo_warning()

eq_list = get_equipment_list()
if not eq_list:
    st.error("Cannot load equipment list.")
    st.stop()

eq_options = {f"{e['equipment_id']} — {e['name']}": e['equipment_id'] for e in eq_list}
selected_label = st.selectbox("Select Equipment", list(eq_options.keys()))
eid = eq_options[selected_label]

eq = get_equipment_detail(eid)
if not eq:
    st.error(f"Cannot load details for {eid}")
    st.stop()

col1, col2 = st.columns([1, 2])

with col1:
    status = eq["status"]
    color = STATUS_COLOR.get(status, "#94A3B8")
    st.markdown(f"""
    <div style="background:#1E293B;border-radius:10px;padding:20px;border:1px solid #334155">
      <h3 style="color:#F97316;margin:0">{eq['name']}</h3>
      <div style="margin:8px 0">
        <span style="color:#94A3B8">ID:</span> <b style="color:#F1F5F9">{eq['equipment_id']}</b>
      </div>
      <div style="margin:4px 0">
        <span style="color:#94A3B8">Type:</span> <b style="color:#F1F5F9">{eq['equipment_type']}</b>
      </div>
      <div style="margin:8px 0">
        <span style="background:{color};padding:3px 10px;border-radius:4px;
        color:#000;font-weight:700;font-size:0.85em">{status}</span>
      </div>
      <div style="margin:8px 0;color:#94A3B8;font-size:0.85em">Mode: 
        <span style="color:#FBBF24">{eq.get('mode','DEMO')}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Input Streams")
    for s in eq.get("input_streams", []):
        st.markdown(f"- `{s}`")
    st.markdown("#### Output Streams")
    for s in eq.get("output_streams", []):
        st.markdown(f"- `{s}`")

with col2:
    params = eq.get("parameters", {})
    if params:
        st.markdown("#### Operating Parameters")
        param_names = list(params.keys())
        param_vals = [float(v) if isinstance(v, (int, float)) else 0 for v in params.values()]
        
        # Gauge-style bar chart
        fig = go.Figure()
        for name, val in params.items():
            if isinstance(val, (int, float)):
                fig.add_trace(go.Bar(
                    x=[name.replace("_", " ").title()],
                    y=[val],
                    text=[f"{val:.1f}"],
                    textposition="outside",
                    marker_color="#38BDF8",
                    showlegend=False,
                ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,1)",
            font=dict(color="#F1F5F9", size=11),
            height=300,
            margin=dict(t=20, b=40, l=20, r=20),
            yaxis=dict(showgrid=True, gridcolor="#1E293B"),
            xaxis=dict(tickangle=-20),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Raw parameters table
        st.markdown("#### Parameter Values")
        rows = [{"Parameter": k.replace("_"," ").title(), "Value": str(v)} for k, v in params.items()]
        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if eq.get("alarms"):
        st.warning(f"🚨 {len(eq['alarms'])} alarm(s) on this equipment")

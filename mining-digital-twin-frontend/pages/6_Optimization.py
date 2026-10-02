"""Page: Optimization Advisory"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import plotly.graph_objects as go

from services.api_client import run_optimization, get_simulation_state
from components.ui_helpers import demo_warning

st.set_page_config(page_title="Optimization Advisory", page_icon="🎯", layout="wide")
st.title("🎯 Optimization Advisory")
demo_warning()

st.warning(
    "⚠️ **DEMO ADVISORY ONLY** — Recommendations are based on simulated/demo data. "
    "These are NOT direct plant control commands. Always validate with process engineers "
    "before any operational changes."
)

objective = st.selectbox("Optimization Objective", [
    "maximize_recovery",
    "maximize_throughput",
    "minimize_water_usage",
    "minimize_energy",
])

if st.button("🚀 Run Optimization Advisory", type="primary"):
    with st.spinner("Running advisory optimization..."):
        result = run_optimization(objective)
    
    if result:
        st.success("✅ Advisory optimization complete")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📋 Recommended Inputs")
            rec = result.get("recommended_inputs", {})
            rows = [{"Parameter": k.replace("_"," ").title(), "Value": str(v)} for k,v in rec.items()]
            import pandas as pd
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        with col2:
            st.markdown("#### 🎯 Expected Outcomes")
            st.metric("Expected Recovery", f"{result.get('expected_recovery_pct',0):.1f}%")
            st.metric("Expected Throughput", f"{result.get('expected_throughput_tph',0):.1f} t/h")
            
            # Compare current vs recommended
            state = get_simulation_state()
            if state:
                curr = state.get("inputs", {})
                params = list(rec.keys())[:5]
                curr_vals = [curr.get(p, 0) for p in params]
                rec_vals = [rec.get(p, 0) for p in params]
                labels = [p.replace("_"," ").title() for p in params]
                
                fig = go.Figure()
                fig.add_trace(go.Bar(name="Current", x=labels, y=curr_vals, marker_color="#334155"))
                fig.add_trace(go.Bar(name="Recommended", x=labels, y=rec_vals, marker_color="#F97316"))
                fig.update_layout(
                    barmode="group",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,1)",
                    font=dict(color="#F1F5F9"), height=300,
                    margin=dict(t=20, b=40, l=20, r=20),
                    legend=dict(font=dict(color="#94A3B8")),
                    yaxis=dict(gridcolor="#1E293B"),
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 💡 Advisory Notes")
        for note in result.get("advisory_notes", []):
            st.markdown(f"- {note}")
        
        st.error(f"🔒 **DISCLAIMER:** {result.get('disclaimer','')}")

else:
    st.info("Select an objective and click **Run Optimization Advisory** to get simulated recommendations.")

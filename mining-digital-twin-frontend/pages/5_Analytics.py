"""Page: Analytics"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from services.api_client import get_mass_balance, get_trends, get_streams_list
from components.ui_helpers import demo_warning

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")
st.title("📈 Analytics & KPIs")
demo_warning()

tab1, tab2, tab3 = st.tabs(["📊 Trends", "⚖️ Mass Balance", "💧 Water Balance"])

# ─── Trends Tab ───────────────────────────────────────────────────────────────
with tab1:
    trends = get_trends()
    if trends:
        st.caption(f"ℹ️ {trends.get('disclaimer','')}")
        ts = trends.get("timestamps", [])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ts, y=trends.get("feed_rate_tph",[]),
            name="Feed Rate (t/h)", line=dict(color="#F97316", width=2.5),
            fill="tozeroy", fillcolor="rgba(249,115,22,0.08)",
        ))
        fig.add_trace(go.Scatter(
            x=ts, y=trends.get("recovery_pct",[]),
            name="Recovery (%)", line=dict(color="#22C55E", width=2.5),
            yaxis="y2",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,1)",
            font=dict(color="#F1F5F9"), height=350,
            margin=dict(t=20, b=40, l=20, r=60),
            yaxis=dict(title="Feed Rate (t/h)", gridcolor="#1E293B"),
            yaxis2=dict(title="Recovery (%)", overlaying="y", side="right", gridcolor="#1E293B"),
            legend=dict(font=dict(color="#94A3B8")),
            xaxis=dict(tickangle=-45),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Mass balance closure trend
        fig2 = go.Figure(go.Scatter(
            x=ts, y=trends.get("mass_balance_closure_pct",[]),
            name="MB Closure %", line=dict(color="#38BDF8", width=2.5),
            fill="tozeroy", fillcolor="rgba(56,189,248,0.08)",
        ))
        fig2.add_hline(y=100, line_color="#F59E0B", line_dash="dash",
                       annotation_text="100% target", annotation_font_color="#F59E0B")
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,1)",
            font=dict(color="#F1F5F9"), height=250,
            margin=dict(t=10, b=40, l=20, r=20),
            yaxis=dict(title="Closure %", gridcolor="#1E293B"),
            title=dict(text="Mass Balance Closure Trend", font=dict(color="#94A3B8", size=13)),
        )
        st.plotly_chart(fig2, use_container_width=True)

# ─── Mass Balance Tab ─────────────────────────────────────────────────────────
with tab2:
    mb = get_mass_balance()
    if mb:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Feed", f"{mb['total_feed_tph']:.1f} t/h")
        c2.metric("Closure", f"{mb['closure_pct']:.1f}%")
        c3.metric("Unaccounted", f"{mb['unaccounted_tph']:.2f} t/h")

        # Waterfall chart
        products = mb.get("product_tph", {})
        cats = ["Feed"] + [k.replace("_"," ").title() for k in products] + ["Tailings","Unaccounted"]
        vals = [mb["total_feed_tph"]]
        for v in products.values():
            vals.append(-v)
        vals.append(-mb["tailings_tph"])
        vals.append(-max(0,mb["unaccounted_tph"]))

        fig = go.Figure(go.Waterfall(
            name="Mass Balance", orientation="v",
            measure=["absolute"] + ["relative"]*(len(cats)-1),
            x=cats, y=vals,
            connector=dict(line=dict(color="#334155")),
            decreasing=dict(marker_color="#F97316"),
            increasing=dict(marker_color="#22C55E"),
            totals=dict(marker_color="#38BDF8"),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,1)",
            font=dict(color="#F1F5F9"), height=380,
            margin=dict(t=20, b=40, l=20, r=20),
            yaxis=dict(title="Mass Flow (t/h)", gridcolor="#1E293B"),
        )
        st.plotly_chart(fig, use_container_width=True)

        if mb.get("warnings"):
            for w in mb["warnings"]:
                st.warning(f"⚠️ {w}")

# ─── Water Balance Tab ────────────────────────────────────────────────────────
with tab3:
    mb = get_mass_balance()
    if mb:
        c1, c2, c3 = st.columns(3)
        c1.metric("Water In", f"{mb.get('water_in_m3h',0):.1f} m³/h")
        c2.metric("Water Out", f"{mb.get('water_out_m3h',0):.1f} m³/h")
        c3.metric("Balance Error", f"{mb.get('water_balance_err_pct',0):.1f}%")

        streams = get_streams_list()
        if streams:
            water_streams = [s for s in streams if s["water_flow_m3h"] > 0]
            df = pd.DataFrame([{
                "Stream": s["stream_id"],
                "Source→Dest": f"{s['source_id']}→{s['destination_id']}",
                "Water (m³/h)": round(s["water_flow_m3h"], 2),
            } for s in water_streams])
            
            fig = px.bar(
                df, x="Stream", y="Water (m³/h)",
                color="Water (m³/h)",
                color_continuous_scale=["#1E3A5F","#38BDF8","#7DD3FC"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,1)",
                font=dict(color="#F1F5F9"), height=300,
                margin=dict(t=20, b=40, l=20, r=20),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

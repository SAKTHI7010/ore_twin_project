"""Shared UI helpers and styling constants."""
import streamlit as st

DEMO_BADGE = "🟡 **DEMO / SIMULATION DATA** — Not validated plant values"

STATUS_COLOR = {
    "RUNNING": "#22C55E",
    "IDLE": "#94A3B8",
    "WARNING": "#F59E0B",
    "FAULT": "#EF4444",
    "SIMULATION": "#38BDF8",
    "ACTIVE": "#22C55E",
}

PRODUCT_COLORS = {
    "pellet": "#F97316",
    "lump_ore": "#A78BFA",
    "ore_fines": "#34D399",
    "middlings": "#FBBF24",
    "reject": "#F87171",
    "tailings": "#94A3B8",
}


def status_badge(status: str) -> str:
    color = STATUS_COLOR.get(status, "#94A3B8")
    return f'<span style="background:{color};padding:2px 8px;border-radius:4px;color:#000;font-weight:600;font-size:0.8em">{status}</span>'


def demo_warning():
    st.warning(DEMO_BADGE)


def metric_card(label: str, value: str, delta: str = "", color: str = "#F97316"):
    st.markdown(
        f"""
        <div style="background:#1E293B;border-radius:8px;padding:16px 20px;border-left:4px solid {color};margin:4px 0;">
            <div style="color:#94A3B8;font-size:0.78em;text-transform:uppercase;letter-spacing:0.08em">{label}</div>
            <div style="font-size:1.6em;font-weight:700;color:#F1F5F9">{value}</div>
            {"<div style='color:#94A3B8;font-size:0.82em'>" + delta + "</div>" if delta else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

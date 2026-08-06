"""
app.py

Streamlit Interactive Dashboard
QAMO — Quantum Adaptive Market Observer

Version : 5.2.0

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dashboard.runner import run_pipeline
from dashboard import (
    page_overview,
    page_classical,
    page_quantum,
    page_entanglement,
    page_qft,
    page_qpe,
    page_optimizer,
    page_report,
    page_live_monitor,
    page_qamo,
    page_qamo_v2,
    page_validation,
)

# ------------------------------------------------------------------
st.set_page_config(
    page_title="QAMO — Quantum Stock Analyzer",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------

with st.sidebar:

    st.title("⚛️ QAMO")
    st.caption("v5.2.0 — Quantum Adaptive Market Observer")

    st.divider()

    st.subheader("Navigation")

    page = st.radio(
        "Page",
        options=[
            "📡 Live Monitor",
            "⚛️ QAMO v2 — Adaptive",
            "⚛️ QAMO v1 — Research Dashboard",
            "🔬 Research Validation",
            "── Portfolio Analysis ──",
            "Portfolio Overview",
            "Classical Analysis",
            "Quantum Encoding & Fidelity",
            "Entanglement",
            "QFT Periodicity",
            "Phase Estimation (QPE)",
            "Portfolio Optimizer (VQC)",
            "Export Report",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # Portfolio setup only for portfolio pages
    _PORTFOLIO_PAGES = {
        "Portfolio Overview", "Classical Analysis",
        "Quantum Encoding & Fidelity", "Entanglement",
        "QFT Periodicity", "Phase Estimation (QPE)",
        "Portfolio Optimizer (VQC)", "Export Report",
    }

    if page in _PORTFOLIO_PAGES:
        st.subheader("Portfolio Setup")

        symbols_input = st.text_input(
            "NSE Symbols (space-separated)",
            value="RELIANCE TCS INFY HDFCBANK",
        )

        days = st.slider(
            "Historical Days",
            min_value=1, max_value=730, value=365, step=1,
        )

        run_btn = st.button("Run Analysis", type="primary", use_container_width=True)
    else:
        symbols_input = ""
        days          = 365
        run_btn       = False

    st.divider()
    st.caption("Data: Yahoo Finance / Zerodha Kite")
    st.caption("Quantum: Qiskit Aer | AI: IBM watsonx")

# ------------------------------------------------------------------
# Pages that need no portfolio pipeline
# ------------------------------------------------------------------

if page == "📡 Live Monitor":
    page_live_monitor.render({})
    st.stop()

if page == "⚛️ QAMO v2 — Adaptive":
    page_qamo_v2.render({})
    st.stop()

if page == "⚛️ QAMO v1 — Research Dashboard":
    page_qamo.render({})
    st.stop()

if page == "🔬 Research Validation":
    page_validation.render({})
    st.stop()

if page == "── Portfolio Analysis ──":
    st.info("Select a portfolio page from the sidebar.")
    st.stop()

# ------------------------------------------------------------------
# Portfolio pipeline
# ------------------------------------------------------------------

if run_btn:
    symbols = [s.strip().upper() for s in symbols_input.split() if s.strip()]
    if len(symbols) < 2:
        st.error("Please enter at least 2 NSE symbols.")
        st.stop()
    try:
        results = run_pipeline(symbols, days)
        st.session_state["results"] = results
        st.session_state["symbols"] = symbols
        st.session_state["days"]    = days
        st.sidebar.success(f"Analysis complete — {len(symbols)} stocks")
    except Exception as ex:
        st.error(f"Pipeline error: {ex}")
        st.stop()

if "results" not in st.session_state:
    st.title("⚛️ QAMO — Quantum Adaptive Market Observer")
    st.subheader("v5.14.0")
    st.markdown("---")
    st.markdown(
        "**Three entry points:**\n\n"
        "- **📡 Live Monitor** — intraday bars, feature vector, price/volume charts\n"
        "- **⚛️ QAMO Research Dashboard** — full 14-stage pipeline for one stock\n"
        "- **🔬 Research Validation** — Classical vs Quantum vs Hybrid comparison\n\n"
        "Or use **Portfolio Analysis** for multi-stock quantum analytics."
    )
    st.stop()

# ------------------------------------------------------------------
# Portfolio pages
# ------------------------------------------------------------------

results = st.session_state["results"]

PAGE_MAP = {
    "Portfolio Overview"          : page_overview,
    "Classical Analysis"          : page_classical,
    "Quantum Encoding & Fidelity" : page_quantum,
    "Entanglement"                : page_entanglement,
    "QFT Periodicity"             : page_qft,
    "Phase Estimation (QPE)"      : page_qpe,
    "Portfolio Optimizer (VQC)"   : page_optimizer,
    "Export Report"               : page_report,
}

PAGE_MAP[page].render(results)

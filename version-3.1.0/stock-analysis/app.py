"""
app.py

Streamlit Interactive Dashboard
Quantum Stock Probability Analyzer

Version : 3.1.0

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
import sys
import os

# Ensure project root is on path
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
)

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------

st.set_page_config(
    page_title="Quantum Stock Analyzer",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------

with st.sidebar:

    st.title("⚛️ Quantum Stock Analyzer")
    st.caption("v3.1.0 — Interactive Dashboard")

    st.divider()

    st.subheader("Portfolio Setup")

    symbols_input = st.text_input(
        "NSE Symbols (space-separated)",
        value="RELIANCE TCS INFY HDFCBANK",
        help="Enter one or more NSE ticker symbols separated by spaces.",
    )

    days = st.slider(
        "Historical Days",
        min_value=1,
        max_value=730,
        value=365,
        step=1,
        help="Number of calendar days of historical data to analyse.",
    )

    run_btn = st.button("Run Analysis", type="primary", use_container_width=True)

    st.divider()

    st.subheader("Navigation")

    page = st.radio(
        "Page",
        options=[
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
    st.caption("Data source: Yahoo Finance (NSE)")
    st.caption("Quantum backend: Qiskit Aer")

# ------------------------------------------------------------------
# Session state — run pipeline
# ------------------------------------------------------------------

if run_btn:
    symbols = [s.strip().upper() for s in symbols_input.split() if s.strip()]
    if len(symbols) < 2:
        st.error("Please enter at least 2 NSE symbols for portfolio analysis.")
        st.stop()

    try:
        results = run_pipeline(symbols, days)
        st.session_state["results"]  = results
        st.session_state["symbols"]  = symbols
        st.session_state["days"]     = days
        st.sidebar.success(f"Analysis complete — {len(symbols)} stocks")
    except Exception as ex:
        st.error(f"Pipeline error: {ex}")
        st.stop()

# ------------------------------------------------------------------
# Guard — require results before rendering pages
# ------------------------------------------------------------------

if "results" not in st.session_state:
    st.title("⚛️ Quantum Stock Probability Analyzer")
    st.subheader("v3.1.0 — Interactive Dashboard")
    st.markdown("---")
    st.markdown(
        "**Getting started:**\n\n"
        "1. Enter NSE symbols in the sidebar (e.g. `RELIANCE TCS INFY HDFCBANK`)\n"
        "2. Choose number of historical days\n"
        "3. Click **Run Analysis**\n\n"
        "The full pipeline runs automatically:\n"
        "classical analysis → quantum encoding → fidelity → "
        "entanglement → QFT → QPE → VQC optimisation"
    )
    st.info("Enter symbols in the sidebar and click **Run Analysis** to begin.")
    st.stop()

# ------------------------------------------------------------------
# Route to page
# ------------------------------------------------------------------

results = st.session_state["results"]

PAGE_MAP = {
    "Portfolio Overview"           : page_overview,
    "Classical Analysis"           : page_classical,
    "Quantum Encoding & Fidelity"  : page_quantum,
    "Entanglement"                 : page_entanglement,
    "QFT Periodicity"              : page_qft,
    "Phase Estimation (QPE)"       : page_qpe,
    "Portfolio Optimizer (VQC)"    : page_optimizer,
    "Export Report"                : page_report,
}

PAGE_MAP[page].render(results)

"""
page_qft.py

Dashboard page — QFT Periodicity Analysis.

Version : 3.1.0
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render(results: dict):

    qft_portfolio = results["qft_portfolio"]
    symbols       = qft_portfolio.symbols()

    st.header("QFT Periodicity Analysis  (v3.1)")

    st.markdown(
        "Daily returns are **amplitude-encoded** into a quantum statevector "
        "and transformed via **Quantum Fourier Transform** (8 qubits, 256 points). "
        "The dominant frequency bins are converted to trading-day periods."
    )

    st.divider()

    # ── Dominant cycle summary ────────────────────────────────────

    st.subheader("Dominant Cycle Summary")

    rows = []
    for sym in symbols:
        qft   = qft_portfolio.get(sym)
        peaks = qft.top_peaks
        rows.append({
            "Symbol"            : sym,
            "Dominant Period"   : f"{peaks[0]['Period']:.1f} days" if peaks else "—",
            "Rank 2 Period"     : f"{peaks[1]['Period']:.1f} days" if len(peaks) > 1 else "—",
            "Rank 3 Period"     : f"{peaks[2]['Period']:.1f} days" if len(peaks) > 2 else "—",
            "Dominant Freq"     : f"{peaks[0]['Frequency']:.4f} cyc/day" if peaks else "—",
            "Magnitude"         : round(peaks[0]["Magnitude"], 6) if peaks else 0,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    sym_s, per_s = qft_portfolio.shortest_cycle()
    sym_l, per_l = qft_portfolio.longest_cycle()

    c1, c2 = st.columns(2)
    c1.metric("Shortest Cycle (most active)", sym_s, f"{per_s:.1f} trading days")
    c2.metric("Longest Cycle (most stable)",  sym_l, f"{per_l:.1f} trading days")

    st.divider()

    # ── Per-stock QFT spectrum ────────────────────────────────────

    st.subheader("QFT Frequency Spectrum — per Stock")

    symbol = st.selectbox("Select Stock", symbols, key="qft_symbol")

    qft   = qft_portfolio.get(symbol)
    peaks = qft.top_peaks

    fig = go.Figure()

    # Plot full magnitude spectrum (first half only)
    mags = qft.magnitudes.copy()
    n    = qft.n_points
    half = n // 2
    freqs = [i / n for i in range(half)]
    fig.add_trace(go.Scatter(
        x=freqs,
        y=list(mags[:half]),
        mode="lines",
        name="QFT Magnitude",
        line=dict(color="#3b82d4", width=1.5),
    ))

    # Highlight top peaks
    for p in peaks:
        if p["Bin"] < half:
            fig.add_trace(go.Scatter(
                x=[p["Frequency"]],
                y=[p["Magnitude"]],
                mode="markers+text",
                text=[f"{p['Period']:.1f}d"],
                textposition="top center",
                marker=dict(size=10, color="#e55c5c"),
                name=f"Rank {p['Rank']} ({p['Period']:.1f} days)",
            ))

    fig.update_layout(
        xaxis_title="Frequency (cycles/day)",
        yaxis_title="Magnitude",
        height=400,
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", y=-0.3),
    )
    st.plotly_chart(fig, width="stretch")

    st.divider()

    # ── Top peaks table ───────────────────────────────────────────

    st.subheader(f"{symbol} — Top 5 Frequency Peaks")

    peak_rows = []
    for p in peaks:
        peak_rows.append({
            "Rank"          : p["Rank"],
            "Bin"           : p["Bin"],
            "Freq (cyc/day)": p["Frequency"],
            "Period (days)" : p["Period"],
            "Magnitude"     : p["Magnitude"],
            "Power"         : p["Power"],
        })

    st.dataframe(
        pd.DataFrame(peak_rows),
        width="stretch",
        hide_index=True,
    )

"""
page_qpe.py

Dashboard page — Quantum Phase Estimation.

Version : 3.1.0
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render(results: dict):

    qpe_portfolio = results["qpe_portfolio"]
    symbols       = qpe_portfolio.symbols()

    st.header("Quantum Phase Estimation  (QPE v3.1)")

    st.markdown(
        "QPE estimates the **eigenphase φ** of U = Ry(θ_q0) for each stock "
        "using **6 counting qubits** (64 phase bins, resolution ≈ 1.56%). "
        "The recovered phase is mapped back to **P(up)** and cross-checked "
        "against the classical value."
    )

    st.divider()

    # ── Summary table ─────────────────────────────────────────────

    st.subheader("QPE Summary")

    rows = []
    for sym in symbols:
        qpe = qpe_portfolio.get(sym)
        rows.append({
            "Symbol"          : sym,
            "Classical P(up)" : round(qpe.p_up_classical, 4),
            "QPE P(up)"       : round(qpe.p_up_estimate, 4),
            "Absolute Error"  : round(qpe.p_up_error(), 4),
            "Phase Estimate φ": round(qpe.phase_estimate, 6),
            "θ Estimate (rad)": round(qpe.theta_estimate, 6),
            "Confidence"      : round(qpe.confidence, 4),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    sym_acc, _ = qpe_portfolio.most_accurate()
    sym_conf, conf = qpe_portfolio.highest_confidence()

    c1, c2 = st.columns(2)
    c1.metric("Most Accurate", sym_acc,
              f"error = {qpe_portfolio.get(sym_acc).p_up_error():.4f}")
    c2.metric("Highest Confidence", sym_conf, f"{conf:.4f}")

    st.divider()

    # ── Classical vs QPE P(up) comparison ────────────────────────

    st.subheader("Classical P(up) vs QPE P(up)")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Classical P(up)",
        x=df["Symbol"],
        y=df["Classical P(up)"],
        marker_color="#3b82d4",
    ))
    fig.add_trace(go.Bar(
        name="QPE P(up)",
        x=df["Symbol"],
        y=df["QPE P(up)"],
        marker_color="#7c5cd8",
    ))
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray",
                  annotation_text="50% (neutral)")
    fig.update_layout(
        barmode="group",
        yaxis_title="P(up)",
        height=380,
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Confidence bar ────────────────────────────────────────────

    st.subheader("QPE Confidence per Stock")

    fig2 = go.Figure(go.Bar(
        x=df["Symbol"],
        y=df["Confidence"],
        marker_color=["#10b981" if v >= 0.8 else
                      "#f59e0b" if v >= 0.5 else "#e55c5c"
                      for v in df["Confidence"]],
        text=[f"{v:.4f}" for v in df["Confidence"]],
        textposition="outside",
    ))
    fig2.add_hline(y=0.8, line_dash="dot", line_color="green",
                   annotation_text="0.8 (high confidence)")
    fig2.update_layout(
        yaxis_title="Confidence",
        yaxis_range=[0, 1.1],
        height=340,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Per-stock phase distribution ──────────────────────────────

    st.subheader("Phase Bin Distribution")

    symbol = st.selectbox("Select Stock", symbols, key="qpe_symbol")
    qpe    = qpe_portfolio.get(symbol)

    probs = qpe.probabilities
    n     = qpe.n_bins
    bins  = list(range(n))
    phases = [j / n for j in bins]

    fig3 = go.Figure(go.Bar(
        x=phases,
        y=list(probs),
        marker_color="#3b82d4",
        opacity=0.8,
    ))

    # Mark top peak
    best_bin = qpe.top_phases[0]["Bin"] if qpe.top_phases else 0
    fig3.add_vline(
        x=best_bin / n,
        line_dash="dash",
        line_color="#e55c5c",
        annotation_text=f"φ_est={qpe.phase_estimate:.4f}",
    )
    fig3.update_layout(
        xaxis_title="Phase φ (normalised)",
        yaxis_title="Probability",
        height=360,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig3, use_container_width=True)

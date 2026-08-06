"""
page_optimizer.py

Dashboard page — VQC Portfolio Optimizer.

Version : 3.1.0
"""

from __future__ import annotations

import math

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd


def render(results: dict):

    optimizer = results["optimizer"]
    allocation = optimizer.allocation()

    st.header("VQC Portfolio Optimizer  (v3.1)")

    st.markdown(
        "**Ansatz :** Ry(encode) → CNOT ring → Ry(variational)  \n"
        "**Cost function :** −Sharpe = −(Σ wᵢμᵢ) / √(wᵀ·Cov·w + ε)  \n"
        "**Optimiser :** COBYLA (derivative-free, scipy)"
    )

    st.divider()

    # ── Key metrics ───────────────────────────────────────────────

    n      = optimizer.n
    eq_w   = np.ones(n) / n
    eq_ret = float(np.dot(eq_w, optimizer.mu))
    eq_var = float(eq_w @ optimizer.cov @ eq_w)
    eq_risk = math.sqrt(max(eq_var, 0.0)) + 1e-8
    eq_sh  = eq_ret / eq_risk
    improvement = (
        (optimizer.optimal_sharpe - eq_sh) / abs(eq_sh)
    ) * 100 if eq_sh != 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sharpe Ratio (VQC)",
              f"{optimizer.optimal_sharpe:.4f}",
              f"{'↑' if improvement >= 0 else '↓'} {abs(improvement):.1f}% vs equal-wt")
    c2.metric("Expected Daily Return",
              f"{optimizer.optimal_return:+.4f}%")
    c3.metric("Portfolio Risk (σ)",
              f"{optimizer.optimal_risk:.4f}")
    c4.metric("Iterations",
              optimizer.n_iterations,
              "Converged" if optimizer.converged else "Max iter reached")

    st.divider()

    # ── Allocation table ──────────────────────────────────────────

    st.subheader("Optimal Portfolio Allocation")

    rows = []
    for row in allocation:
        rows.append({
            "Symbol"         : row["Symbol"],
            "Weight"         : row["Weight"],
            "Weight %"       : f"{row['WeightPct']:.2f}%",
            "Return Contrib %": f"{row['ReturnContrib']:.4f}",
            "Recommendation" : row["Recommendation"],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Pie chart ─────────────────────────────────────────────────

    st.subheader("Portfolio Weight Distribution")

    fig = go.Figure(go.Pie(
        labels=[r["Symbol"] for r in allocation],
        values=[r["Weight"] for r in allocation],
        hole=0.4,
        textinfo="label+percent",
        marker=dict(colors=[
            "#3b82d4", "#7c5cd8", "#10b981",
            "#f59e0b", "#e55c5c", "#06b6d4", "#f97316"
        ]),
    ))
    fig.update_layout(height=400, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # ── Bar: VQC vs Equal-weight ──────────────────────────────────

    st.subheader("VQC Weights vs Equal-Weight Benchmark")

    syms    = [r["Symbol"] for r in allocation]
    vqc_w   = [r["Weight"] for r in allocation]
    eq_each = 1.0 / len(syms)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name="VQC Weight",
        x=syms, y=vqc_w,
        marker_color="#3b82d4",
        text=[f"{v:.4f}" for v in vqc_w],
        textposition="outside",
    ))
    fig2.add_hline(
        y=eq_each,
        line_dash="dash",
        line_color="#e55c5c",
        annotation_text=f"Equal-weight ({eq_each:.4f})",
    )
    fig2.update_layout(
        yaxis_title="Portfolio Weight",
        height=360,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Sharpe comparison table ───────────────────────────────────

    st.subheader("VQC vs Equal-Weight Benchmark")

    cmp = pd.DataFrame([
        {"Metric": "Expected Return",
         "VQC": f"{optimizer.optimal_return:+.4f}%",
         "Equal-Weight": f"{eq_ret:+.4f}%"},
        {"Metric": "Portfolio Risk (σ)",
         "VQC": f"{optimizer.optimal_risk:.4f}",
         "Equal-Weight": f"{eq_risk:.4f}"},
        {"Metric": "Sharpe Ratio",
         "VQC": f"{optimizer.optimal_sharpe:.4f}",
         "Equal-Weight": f"{eq_sh:.4f}"},
    ])
    st.dataframe(cmp, use_container_width=True, hide_index=True)

    arrow = "↑" if improvement >= 0 else "↓"
    st.success(
        f"Sharpe improvement vs equal-weight: "
        f"**{arrow} {abs(improvement):.1f}%**"
    )

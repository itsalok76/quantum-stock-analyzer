"""
page_quantum.py

Dashboard page — Quantum Encoding & Fidelity.

Version : 3.1.0
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render(results: dict):

    quantum_portfolio = results["quantum_portfolio"]
    fidelity          = results["fidelity"]
    symbols           = quantum_portfolio.symbols()

    st.header("Quantum Encoding & Fidelity")

    st.markdown(
        "Each stock is encoded as a **5-qubit product state** "
        "|ψ⟩ = |q0⟩ ⊗ |q1⟩ ⊗ |q2⟩ ⊗ |q3⟩ ⊗ |q4⟩. "
        "Each qubit independently encodes one market feature via Ry rotation."
    )

    LABELS = ["Probability", "Volatility", "Momentum", "Trend", "Volume"]

    st.divider()

    # ── Encoding table ────────────────────────────────────────────

    st.subheader("Qubit Encoding Table")

    rows = []
    for sym in symbols:
        state = quantum_portfolio.get_state(sym)
        row   = {"Symbol": sym}
        for i, label in enumerate(LABELS):
            row[f"q{i} Ry (rad)"] = round(state.angles[i], 4)
            row[f"q{i} P(|1>)"]   = round(state.qubit_prob_one(i), 4)
        rows.append(row)

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
    )

    st.divider()

    # ── Per-stock qubit probability radar ─────────────────────────

    st.subheader("Qubit P(|1>) per Stock")

    fig = go.Figure()

    colours = ["#3b82d4", "#7c5cd8", "#10b981", "#f59e0b",
               "#e55c5c", "#06b6d4", "#f97316"]

    for i, sym in enumerate(symbols):
        state = quantum_portfolio.get_state(sym)
        probs = [state.qubit_prob_one(q) for q in range(5)]
        fig.add_trace(go.Bar(
            name=sym,
            x=[f"q{q} {LABELS[q]}" for q in range(5)],
            y=probs,
            marker_color=colours[i % len(colours)],
        ))

    fig.update_layout(
        barmode="group",
        yaxis_title="P(|1>)",
        height=380,
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig, width="stretch")

    st.divider()

    # ── Fidelity matrix heatmap ───────────────────────────────────

    st.subheader("Quantum Fidelity Matrix  F(ψᵢ, ψⱼ) = |⟨ψᵢ|ψⱼ⟩|²")

    st.markdown(
        "**Interpretation :** "
        "1.0 = identical states · "
        "> 0.95 = very similar · "
        "< 0.80 = different quantum profiles"
    )

    mat = fidelity.matrix

    fig2 = go.Figure(go.Heatmap(
        z=mat.values,
        x=list(mat.columns),
        y=list(mat.index),
        colorscale="Blues",
        zmin=0, zmax=1,
        text=mat.round(4).values,
        texttemplate="%{text}",
    ))
    fig2.update_layout(height=420, margin=dict(t=20, b=20))
    st.plotly_chart(fig2, width="stretch")

    st.divider()

    # ── Pairwise fidelity bar chart ───────────────────────────────

    st.subheader("Pairwise Fidelity Rankings")

    pairs, fvals = [], []
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            pairs.append(f"{symbols[i]} ↔ {symbols[j]}")
            fvals.append(round(float(mat.iloc[i, j]), 6))

    pairs_sorted = sorted(zip(pairs, fvals), key=lambda x: -x[1])
    p_labels = [x[0] for x in pairs_sorted]
    p_values = [x[1] for x in pairs_sorted]

    fig3 = go.Figure(go.Bar(
        x=p_labels,
        y=p_values,
        marker_color=["#3b82d4" if v > 0.9 else
                      "#7c5cd8" if v > 0.8 else "#e55c5c"
                      for v in p_values],
        text=[f"{v:.4f}" for v in p_values],
        textposition="outside",
    ))
    fig3.add_hline(y=0.95, line_dash="dot", line_color="green",
                   annotation_text="0.95 (very similar)")
    fig3.add_hline(y=0.80, line_dash="dot", line_color="orange",
                   annotation_text="0.80 (moderately similar)")
    fig3.update_layout(
        yaxis_title="Fidelity",
        yaxis_range=[0, 1.05],
        height=380,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig3, width="stretch")

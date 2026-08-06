"""
page_entanglement.py

Dashboard page — Portfolio Entanglement Analysis.

Version : 3.1.0
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render(results: dict):

    entanglement = results["entanglement"]
    pairs        = entanglement.pairs

    st.header("Portfolio Entanglement  (CNOT v3.1)")

    st.markdown(
        "Two stocks are quantum-entangled via a **CNOT gate** on their "
        "q0 (Probability) qubits. "
        "**Entropy** (von Neumann): 0 = separable, 1 = maximally entangled. "
        "**Concurrence**: 0 = separable, 1 = Bell state. "
        "**Bell State**: closest of Φ+, Φ−, Ψ+, Ψ−."
    )

    st.divider()

    # ── Pairs table ───────────────────────────────────────────────

    st.subheader("Pairwise Entanglement Metrics")

    rows = []
    for p in pairs:
        rows.append({
            "Pair"             : f"{p.symbol_a} ↔ {p.symbol_b}",
            "Entropy"          : round(p.entropy, 6),
            "Concurrence"      : round(p.concurrence, 6),
            "Bell State"       : p.bell_state,
            "Classical Corr"   : round(p.classical_corr, 4),
            "Dominant"         : (
                "Quantum > Classical"
                if p.concurrence > abs(p.classical_corr)
                else "Classical ≥ Quantum"
            ),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    st.divider()

    # ── Entropy vs Classical correlation scatter ──────────────────

    st.subheader("Quantum Entanglement vs Classical Correlation")

    fig = go.Figure()

    bell_colours = {
        "Φ+": "#3b82d4", "Φ−": "#7c5cd8",
        "Ψ+": "#10b981", "Ψ−": "#f59e0b",
    }

    for p in pairs:
        fig.add_trace(go.Scatter(
            x=[p.classical_corr],
            y=[p.concurrence],
            mode="markers+text",
            name=f"{p.symbol_a}↔{p.symbol_b}",
            text=[f"{p.symbol_a}↔{p.symbol_b}"],
            textposition="top center",
            marker=dict(
                size=14,
                color=bell_colours.get(p.bell_state, "#aaa"),
                symbol="circle",
            ),
        ))

    fig.add_shape(
        type="line",
        x0=0, y0=0, x1=1, y1=1,
        line=dict(dash="dot", color="gray"),
    )
    fig.add_annotation(
        x=0.5, y=0.52, text="Quantum = Classical",
        showarrow=False, font=dict(color="gray", size=11),
    )
    fig.update_layout(
        xaxis_title="Classical Pearson Correlation",
        yaxis_title="Quantum Concurrence",
        height=440,
        margin=dict(t=20, b=20),
        showlegend=True,
        legend=dict(orientation="h", y=-0.3),
    )
    st.plotly_chart(fig, width="stretch")

    st.divider()

    # ── Entropy matrix heatmap ────────────────────────────────────

    st.subheader("Entanglement Entropy Matrix")

    ent_df = entanglement.entropy_dataframe()
    fig2   = go.Figure(go.Heatmap(
        z=ent_df.values,
        x=list(ent_df.columns),
        y=list(ent_df.index),
        colorscale="Purples",
        text=ent_df.round(4).values,
        texttemplate="%{text}",
    ))
    fig2.update_layout(height=380, margin=dict(t=20, b=20))
    st.plotly_chart(fig2, width="stretch")

    st.divider()

    # ── Highlight ─────────────────────────────────────────────────

    hi = entanglement.highest_entanglement()
    lo = entanglement.lowest_entanglement()

    c1, c2 = st.columns(2)
    c1.metric(
        "Highest Entanglement",
        f"{hi.symbol_a} ↔ {hi.symbol_b}",
        f"entropy={hi.entropy:.4f}  conc={hi.concurrence:.4f}",
    )
    c2.metric(
        "Lowest Entanglement",
        f"{lo.symbol_a} ↔ {lo.symbol_b}",
        f"entropy={lo.entropy:.4f}  conc={lo.concurrence:.4f}",
    )

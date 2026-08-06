"""
page_overview.py

Dashboard page — Portfolio Overview.

Version : 3.1.0
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render(results: dict):

    portfolio   = results["portfolio"]
    comparison  = results["comparison"]
    correlation = results["correlation"]
    symbols     = portfolio.get_symbols()

    st.header("Portfolio Overview")

    # ── Top metric cards ─────────────────────────────────────────

    best  = comparison.best_probability()
    risk  = comparison.lowest_risk()
    gain  = comparison.highest_gain()
    s1h, s2h, ch = correlation.highest_pair()
    s1l, s2l, cl = correlation.lowest_pair()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Highest P(Close>Open)",  best["Symbol"],
              f"{best['ProbabilityUp']:.2f}%")
    c2.metric("Lowest Volatility",    risk["Symbol"],
              f"{risk['Volatility']:.4f}")
    c3.metric("Highest Avg Gain",     gain["Symbol"],
              f"{gain['AverageGain']:.2f}%")
    c4.metric("Highest Correlation",  f"{s1h} ↔ {s2h}",
              f"{ch:.3f}")

    st.divider()

    # ── Portfolio comparison table ────────────────────────────────

    st.subheader("Portfolio Comparison")

    rows = []
    for sym in symbols:
        s = portfolio.get_analyzer(sym).get_summary()
        rows.append({
            "Symbol"              : sym,
            "P(Close>Open) %"     : round(s["ProbabilityUp"] * 100, 2),
            "P(Open>Close) %"     : round(s["ProbabilityDown"] * 100, 2),
            "Avg Gain %"          : round(s["AverageGain"], 2),
            "Avg Loss %"          : round(s["AverageLoss"], 2),
            "Volatility"          : round(s["Volatility"], 4),
            "Green Days"          : s["GreenDays"],
            "Red Days"            : s["RedDays"],
            "Trend Slope"         : round(s.get("TrendSlope", 0), 4),
            "Avg Vol (M)"         : round(s.get("AverageVolume", 0), 2),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    st.divider()

    # ── P(Close>Open) bar chart ───────────────────────────────────

    st.subheader("P(Close > Open) — Intraday Up Probability")
    st.caption("Probability that the stock's **closing price is higher than its opening price** on a given trading day.")

    fig = go.Figure(go.Bar(
        x=df["Symbol"],
        y=df["P(Close>Open) %"],
        marker_color=["#3b82d4" if v >= 50 else "#e55c5c"
                      for v in df["P(Close>Open) %"]],
        text=[f"{v:.2f}%" for v in df["P(Close>Open) %"]],
        textposition="outside",
    ))
    fig.add_hline(y=50, line_dash="dash", line_color="gray",
                  annotation_text="50% (neutral)")
    fig.update_layout(
        yaxis_title="P(Close > Open) %",
        showlegend=False,
        height=380,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig, width="stretch")

    # ── Volatility comparison ─────────────────────────────────────

    st.subheader("Volatility Comparison")

    fig2 = go.Figure(go.Bar(
        x=df["Symbol"],
        y=df["Volatility"],
        marker_color="#7c5cd8",
        text=[f"{v:.4f}" for v in df["Volatility"]],
        textposition="outside",
    ))
    fig2.update_layout(
        yaxis_title="Volatility (σ)",
        showlegend=False,
        height=340,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig2, width="stretch")

    st.divider()

    # ── Correlation heatmap ───────────────────────────────────────

    st.subheader("Classical Correlation Matrix")

    corr_df = correlation.correlation
    fig3 = go.Figure(go.Heatmap(
        z=corr_df.values,
        x=list(corr_df.columns),
        y=list(corr_df.index),
        colorscale="Blues",
        zmin=-1, zmax=1,
        text=corr_df.round(3).values,
        texttemplate="%{text}",
    ))
    fig3.update_layout(height=400, margin=dict(t=20, b=20))
    st.plotly_chart(fig3, width="stretch")

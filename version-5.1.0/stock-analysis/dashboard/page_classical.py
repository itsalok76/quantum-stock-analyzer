"""
page_classical.py

Dashboard page — Individual Stock Classical Analysis.

Version : 3.1.0
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

from insights import InsightEngine
from config import OUTPUT_CHART_DIR


def render(results: dict):

    portfolio = results["portfolio"]
    symbols   = portfolio.get_symbols()

    st.header("Individual Stock Analysis")

    symbol = st.selectbox("Select Stock", symbols, key="classical_symbol")

    analyzer = portfolio.get_analyzer(symbol)
    summary  = analyzer.get_summary()
    df       = analyzer.get_dataframe()
    insight  = InsightEngine(summary)

    st.divider()

    # ── Metric cards ──────────────────────────────────────────────

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Trading Days", summary["TradingDays"])
    c2.metric("P(Close > Open)",
              f"{summary['ProbabilityUp']*100:.2f}%",
              help="Probability that Close > Open (intraday)")
    c3.metric("Volatility",
              f"{summary['Volatility']:.4f}")
    c4.metric("Avg Gain",
              f"{summary['AverageGain']:.2f}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Green Days", summary["GreenDays"])
    c6.metric("Red Days", summary["RedDays"])
    c7.metric("Max Gain", f"{summary['MaxGain']:.2f}%")
    c8.metric("Max Loss", f"{summary['MaxLoss']:.2f}%")

    st.divider()

    # ── Price chart ───────────────────────────────────────────────

    st.subheader(f"{symbol} — Price & Moving Averages")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Close"],
        name="Close", line=dict(color="#1f2328", width=1.5)
    ))
    for ma, colour in [(20, "#3b82d4"), (50, "#f59e0b"), (100, "#10b981")]:
        col = f"MA_{ma}"
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date"], y=df[col],
                name=f"MA {ma}", line=dict(color=colour, width=1, dash="dot")
            ))
    fig.update_layout(
        xaxis_title="Date", yaxis_title="Price (₹)",
        height=400, margin=dict(t=20, b=20),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Returns histogram ─────────────────────────────────────────

    st.subheader(f"{symbol} — Daily Return Distribution")

    returns = df["PercentChange"].dropna()
    fig2 = go.Figure(go.Histogram(
        x=returns,
        nbinsx=50,
        marker_color="#3b82d4",
        opacity=0.8,
    ))
    fig2.add_vline(x=0, line_dash="dash", line_color="red")
    fig2.update_layout(
        xaxis_title="Daily Return (%)",
        yaxis_title="Frequency",
        height=340,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Volume chart ──────────────────────────────────────────────

    st.subheader(f"{symbol} — Trading Volume")

    fig3 = go.Figure(go.Bar(
        x=df["Date"],
        y=df["Volume"],
        marker_color="#7c5cd8",
        opacity=0.7,
    ))
    fig3.update_layout(
        xaxis_title="Date",
        yaxis_title="Volume",
        height=300,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── Full stats table ──────────────────────────────────────────

    st.subheader("Full Statistics")

    stats = {
        "Trading Days"        : summary["TradingDays"],
        "Green Days"          : summary["GreenDays"],
        "Red Days"            : summary["RedDays"],
        "P(Close > Open)"     : f"{summary['ProbabilityUp']*100:.2f}%",
        "P(Open > Close)"     : f"{summary['ProbabilityDown']*100:.2f}%",
        "Average Open"        : f"₹{summary['AverageOpen']:.2f}",
        "Average Close"       : f"₹{summary['AverageClose']:.2f}",
        "Average Gain"        : f"{summary['AverageGain']:.2f}%",
        "Average Loss"        : f"{summary['AverageLoss']:.2f}%",
        "Max Gain"            : f"{summary['MaxGain']:.2f}%",
        "Max Loss"            : f"{summary['MaxLoss']:.2f}%",
        "Volatility"          : f"{summary['Volatility']:.4f}",
        "Std Dev"             : f"{summary['StdDev']:.4f}",
        "Longest Green Streak": f"{summary['LongestGreenStreak']} days",
        "Longest Red Streak"  : f"{summary['LongestRedStreak']} days",
        "Trend Slope"         : f"{summary.get('TrendSlope', 0):.4f}% /day",
        "Avg Volume"          : f"{summary.get('AverageVolume', 0):.2f}M",
    }

    st.dataframe(
        pd.DataFrame(stats.items(), columns=["Metric", "Value"]),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ── Insight ───────────────────────────────────────────────────

    st.subheader("Insight")

    rec = insight.recommendation()
    colour = {
        "STRONG BUY": "green",
        "BUY"       : "blue",
        "HOLD"      : "orange",
        "SELL"      : "red",
    }.get(rec, "gray")

    st.markdown(
        f"**Recommendation : "
        f"<span style='color:{colour}'>{rec}</span>**",
        unsafe_allow_html=True,
    )

    for line in insight.executive_summary().split("\n"):
        st.markdown(f"> {line}")

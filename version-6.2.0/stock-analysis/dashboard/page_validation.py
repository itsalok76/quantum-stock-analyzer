"""
page_validation.py

Stage 14 — Research Validation Dashboard.

Runs Classical ML vs Quantum Model vs Hybrid side-by-side
on the same intraday bar history and presents a comparison table.

Version : 5.14.0
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from live.yahoo_feed       import YahooFeed
from live.tick_buffer      import TickBuffer
from live.validation_engine import ValidationEngine


def render(results: dict):

    st.title("🔬 Research Validation")
    st.caption(
        "v5.14.0 · Stage 14 — Classical ML vs Quantum vs Hybrid  |  "
        "Same intraday data, three models, side-by-side metrics."
    )

    st.divider()

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    symbol   = c1.text_input("NSE Symbol", value="RELIANCE").strip().upper()
    interval = c2.selectbox("Interval", ["5m", "15m", "30m", "1m"])
    n_bars   = c3.number_input("Bars", min_value=50, max_value=500, value=200, step=50)
    top_k    = c4.number_input("Top-k", min_value=5, max_value=50, value=20, step=5)

    run_btn = st.button("▶  Run Validation", type="primary")

    st.divider()

    if not run_btn and f"val_result_{symbol}" not in st.session_state:
        st.info(
            "Select a symbol and click **Run Validation** to compare "
            "Classical ML, Quantum QAMO, and Hybrid models on the same data."
        )
        return

    if run_btn:
        with st.spinner(f"Fetching {symbol} ({interval}) data..."):
            feed = YahooFeed(symbol, interval)
            bars = feed.fetch_latest(n_bars=n_bars)

        if not bars:
            st.error("No data returned.")
            return

        with st.spinner("Running walk-forward validation (3 models)..."):
            ve     = ValidationEngine(symbol, bars, interval, top_k=int(top_k))
            result = ve.run()
            st.session_state[f"val_result_{symbol}"] = result

    result = st.session_state.get(f"val_result_{symbol}", {})
    if not result:
        return

    comp = result.get("comparison", {})

    # ------------------------------------------------------------------
    # Summary comparison table
    # ------------------------------------------------------------------
    st.subheader("Model Comparison")

    metrics = [
        ("Directional Accuracy (%)", "directional_accuracy"),
        ("Sharpe Ratio",             "sharpe_ratio"),
        ("Win Rate (%)",             "win_rate"),
        ("Total Return (%)",         "total_return_pct"),
        ("Max Drawdown (%)",         "max_drawdown_pct"),
        ("Avg Latency (ms)",         "avg_latency_ms"),
    ]

    rows = []
    for label, key in metrics:
        row = {"Metric": label}
        for model in ["classical", "quantum", "hybrid"]:
            v = comp.get(model, {}).get(key, "—")
            row[model.capitalize()] = v if v == "—" else round(float(v), 3)
        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    # ------------------------------------------------------------------
    # Winner highlight
    # ------------------------------------------------------------------
    st.subheader("Best Model by Metric")
    for label, key in metrics[:4]:   # top 4 metrics
        vals = {
            m: comp.get(m, {}).get(key)
            for m in ["classical", "quantum", "hybrid"]
            if comp.get(m, {}).get(key) is not None
        }
        if not vals:
            continue
        if key == "max_drawdown_pct":
            winner = min(vals, key=vals.get)
        else:
            winner = max(vals, key=vals.get)
        st.markdown(f"**{label}** → 🏆 `{winner.capitalize()}` "
                    f"({vals[winner]:.3f})")

    # ------------------------------------------------------------------
    # Per-model detail
    # ------------------------------------------------------------------
    st.subheader("Detailed Results")
    for model in ["classical", "quantum", "hybrid"]:
        with st.expander(f"{model.capitalize()} Model"):
            mdata = comp.get(model, {})
            if not mdata:
                st.info("No data.")
                continue
            rows2 = [{"Metric": k, "Value": v} for k, v in mdata.items()]
            st.dataframe(pd.DataFrame(rows2), width="stretch", hide_index=True)

    st.caption(
        f"Walk-forward on {result['n_bars']} bars of {symbol}.NS  "
        f"({interval} interval). Classical baseline = RSI + MACD + EMA crossover. "
        "Quantum = QAMO similarity search. Hybrid = Quantum filtered by confidence ≥ 40%."
    )

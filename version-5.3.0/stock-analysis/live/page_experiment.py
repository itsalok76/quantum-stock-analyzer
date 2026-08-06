"""
page_experiment.py

Stage — Quantum Trajectory Experiment Dashboard (v6.1.0).

Two tabs:
    Tab 1 — Single Day Experiment
        Pick symbol + date + training window + fwd_bars + min_confidence
        → run static + adaptive
        Show all 4 charts + metrics table (incl. dir_accuracy_filtered) + df

    Tab 2 — Walk-Forward Validation
        Pick symbol + date range + training window → run over all days
        Show aggregate summary + per-day table + delta comparison

Version : 6.1.0
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import streamlit as st

from live.experiment_runner import ExperimentRunner
from live.walk_forward       import WalkForwardValidator
from live.trading_calendar   import is_trading_day, previous_trading_days


# ------------------------------------------------------------------

def render(results: dict):

    st.title("🧪 Trajectory Experiment")
    st.caption(
        "v6.1.0 · Static vs Adaptive intraday prediction · "
        "5-min bars · fwd_bars return window · confidence threshold filter · "
        "Walk-forward validation · No look-ahead bias"
    )

    st.divider()

    tab1, tab2 = st.tabs([
        "📅 Single Day Experiment",
        "📈 Walk-Forward Validation",
    ])

    with tab1:
        _render_single_day()

    with tab2:
        _render_walk_forward()


# ------------------------------------------------------------------
# Tab 1 — Single Day
# ------------------------------------------------------------------

def _render_single_day():

    st.subheader("Single Day Prediction Experiment")

    c1, c2, c3 = st.columns([2, 2, 1])

    symbol = c1.text_input(
        "NSE Symbol", value="RELIANCE", key="exp_symbol"
    ).strip().upper()

    pred_date = c2.date_input(
        "Prediction Date",
        value=date.today() - timedelta(days=1),
        key="exp_date",
    )

    top_k = c3.number_input(
        "Top-k", min_value=5, max_value=50, value=20, step=5,
        key="exp_topk",
    )

    c4, c5, c6 = st.columns([1, 1, 1])

    n_days = c4.number_input(
        "Training Days",
        min_value=10, max_value=100, value=30, step=5,
        key="exp_ndays",
        help="Yahoo Finance 5-min: use ≤30 for reliable data.",
    )

    fwd_bars = c5.number_input(
        "Fwd Bars",
        min_value=1, max_value=10, value=3, step=1,
        key="exp_fwdbars",
        help="Bars ahead used to measure return in memory search (default 3). "
             "Higher = stronger directional signal but fewer valid matches near end-of-day.",
    )

    min_confidence = c6.slider(
        "Min Confidence",
        min_value=0.0, max_value=1.0, value=0.10, step=0.05,
        key="exp_minconf",
        help="Only bars with model confidence ≥ this value emit a directional signal. "
             "Bars below threshold are held flat and excluded from dir_accuracy_filtered.",
    )

    run_btn = st.button("▶  Run Experiment", type="primary", key="exp_run")

    # Validate date
    if not is_trading_day(pred_date):
        st.warning(f"{pred_date} is not a trading day. Choose a weekday that is not a holiday.")

    if run_btn:
        progress_area = st.empty()
        log_lines     = []

        def _log(msg: str):
            log_lines.append(msg)
            progress_area.text("\n".join(log_lines[-6:]))

        with st.spinner("Running experiment..."):
            runner = ExperimentRunner(
                symbol          = symbol,
                prediction_date = pred_date,
                n_training_days = int(n_days),
                interval        = "5m",
                top_k           = int(top_k),
                fwd_bars        = int(fwd_bars),
                min_confidence  = float(min_confidence),
            )
            exp = runner.run(progress_cb=_log)

        progress_area.empty()

        if exp.error:
            st.error(f"Experiment failed: {exp.error}")
            return

        st.session_state["exp_result"] = exp

    exp = st.session_state.get("exp_result")
    if exp is None:
        st.info("Configure the experiment above and click **▶ Run Experiment**.")
        return

    # ------------------------------------------------------------------
    # Results header
    # ------------------------------------------------------------------
    st.success(
        f"**{exp.symbol}** · {exp.prediction_date} · "
        f"{exp.n_training_bars:,} training bars · "
        f"{exp.n_prediction_bars} prediction bars (5-min)"
    )

    # ------------------------------------------------------------------
    # Metrics comparison table
    # ------------------------------------------------------------------
    st.subheader("📊 Benchmark Metrics — Static vs Adaptive")

    # Signal coverage info
    s_sig  = exp.static.metrics.get("signal_rate",    100.0)
    a_sig  = exp.adaptive.metrics.get("signal_rate",  100.0)
    s_nb   = exp.static.metrics.get("n_signal_bars",  "—")
    a_nb   = exp.adaptive.metrics.get("n_signal_bars","—")
    st.caption(
        f"Signal coverage — Static: **{s_sig:.1f}%** ({s_nb} bars with signal)  |  "
        f"Adaptive: **{a_sig:.1f}%** ({a_nb} bars with signal)  |  "
        f"Min confidence threshold: **{min_confidence:.2f}**  |  "
        f"Fwd bars: **{int(fwd_bars)}**"
    )

    metric_labels = {
        "avg_fidelity"         : "Avg Fidelity F(ψ̂, ψ)",
        "dir_accuracy"         : "Dir Accuracy % (all bars)",
        "dir_accuracy_filtered": "⭐ Dir Accuracy % (signal bars only)",
        "signal_rate"          : "Signal Rate %",
        "mae"                  : "MAE %",
        "rmse"                 : "RMSE %",
        "avg_confidence"       : "Avg Confidence",
        "entropy_accuracy"     : "Entropy Accuracy %",
        "sharpe_ratio"         : "Sharpe Ratio (signal bars)",
    }

    mrows = []
    for key, label in metric_labels.items():
        sv = exp.static.metrics.get(key,   "—")
        av = exp.adaptive.metrics.get(key, "—")
        dk = f"delta_{key}"
        dv = exp.delta.get(dk, "—")
        better = ""
        if isinstance(dv, float):
            better = "✅ Adaptive" if dv > 0 else ("⚠️ Static" if dv < 0 else "—")
            dv     = f"{dv:+.4f}"
        mrows.append({
            "Metric"         : label,
            "Static"         : sv,
            "Adaptive"       : av,
            "Δ (Adaptive−Static)": dv,
            "Better"         : better,
        })

    st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True)

    st.divider()

    # ------------------------------------------------------------------
    # Chart 1 — Price trajectory
    # ------------------------------------------------------------------
    st.subheader("Chart 1 — Price Trajectory")

    if exp.static.actual_closes and exp.static.predicted_closes:
        ts     = exp.static.timestamps
        n      = min(len(ts), len(exp.static.actual_closes),
                     len(exp.static.predicted_closes),
                     len(exp.adaptive.predicted_closes))
        pdf = pd.DataFrame({
            "Actual"         : exp.static.actual_closes[:n],
            "Static Pred"    : exp.static.predicted_closes[:n],
            "Adaptive Pred"  : exp.adaptive.predicted_closes[:n],
        }, index=[t[:16] for t in ts[:n]])
        st.line_chart(pdf, height=260)
        st.caption(
            "Actual close · Static prediction (morning forecast, no updates) · "
            "Adaptive prediction (bar-by-bar self-correction)"
        )

    # ------------------------------------------------------------------
    # Chart 2 — Fidelity over time
    # ------------------------------------------------------------------
    st.subheader("Chart 2 — Fidelity F(ψ̂(t), ψ(t))")

    s_fid = exp.static.comparison_df["fidelity"].dropna().tolist()   \
            if not exp.static.comparison_df.empty else []
    a_fid = exp.adaptive.comparison_df["fidelity"].dropna().tolist() \
            if not exp.adaptive.comparison_df.empty else []

    if s_fid or a_fid:
        nf = min(len(s_fid), len(a_fid)) if s_fid and a_fid else max(len(s_fid), len(a_fid))
        fdf = pd.DataFrame({
            "Static Fidelity"  : s_fid[:nf] if s_fid else [None] * nf,
            "Adaptive Fidelity": a_fid[:nf] if a_fid else [None] * nf,
        })
        st.line_chart(fdf, height=220)
        st.caption("1.0 = perfect state prediction. Higher adaptive fidelity → self-correction is working.")

    # ------------------------------------------------------------------
    # Chart 3 — Confidence over time
    # ------------------------------------------------------------------
    st.subheader("Chart 3 — Model Confidence")

    s_conf = exp.static.confidences
    a_conf = exp.adaptive.confidences
    if s_conf or a_conf:
        nc = min(len(s_conf), len(a_conf)) if s_conf and a_conf else max(len(s_conf), len(a_conf))
        cdf = pd.DataFrame({
            "Static Confidence"  : s_conf[:nc] if s_conf else [None] * nc,
            "Adaptive Confidence": a_conf[:nc] if a_conf else [None] * nc,
        })
        st.line_chart(cdf, height=200)

    # ------------------------------------------------------------------
    # Chart 4 — Entropy: predicted vs actual
    # ------------------------------------------------------------------
    st.subheader("Chart 4 — State Entropy (Predicted vs Actual)")

    a_pe = exp.adaptive.pred_entropy
    a_ae = exp.adaptive.actual_entropy
    if a_pe and a_ae:
        ne = min(len(a_pe), len(a_ae))
        edf = pd.DataFrame({
            "Predicted Entropy": a_pe[:ne],
            "Actual Entropy"   : a_ae[:ne],
        })
        st.line_chart(edf, height=200)
        st.caption("Does the model correctly detect Stable → Volatile → Chaotic transitions?")

    # ------------------------------------------------------------------
    # Per-bar comparison table
    # ------------------------------------------------------------------
    with st.expander("Per-Bar Comparison Table (Adaptive Mode)"):
        if not exp.adaptive.comparison_df.empty:
            st.dataframe(
                exp.adaptive.comparison_df.head(50),
                use_container_width=True,
                hide_index=True,
            )


# ------------------------------------------------------------------
# Tab 2 — Walk-Forward
# ------------------------------------------------------------------

def _render_walk_forward():

    st.subheader("Walk-Forward Validation")
    st.caption(
        "Runs the experiment for every trading day in the date range. "
        "Computes aggregate metrics across all days. "
        "Use ⭐ Dir Accuracy (signal bars only) as the primary trust metric."
    )

    c1, c2, c3 = st.columns([2, 1, 1])
    symbol     = c1.text_input("NSE Symbol", value="RELIANCE", key="wf_symbol").strip().upper()
    start_date = c2.date_input("Start Date", value=date.today() - timedelta(days=14), key="wf_start")
    end_date   = c3.date_input("End Date",   value=date.today() - timedelta(days=1),  key="wf_end")

    c4, c5, c6 = st.columns([1, 1, 1])
    n_days = c4.number_input(
        "Training Days", min_value=10, max_value=60, value=30, step=5,
        key="wf_ndays",
        help="Keep ≤30 for Yahoo Finance 5-min data availability.",
    )
    fwd_bars = c5.number_input(
        "Fwd Bars", min_value=1, max_value=10, value=3, step=1,
        key="wf_fwdbars",
        help="Bars ahead for pct_change in memory search. Match the single-day experiment setting.",
    )
    min_confidence = c6.slider(
        "Min Confidence", min_value=0.0, max_value=1.0, value=0.10, step=0.05,
        key="wf_minconf",
        help="Confidence threshold for signal emission. Match the single-day experiment setting.",
    )

    run_btn = st.button("▶  Run Walk-Forward", type="primary", key="wf_run")

    if run_btn:
        progress_area = st.empty()
        log_lines     = []

        def _log(msg: str):
            log_lines.append(msg)
            progress_area.text("\n".join(log_lines[-8:]))

        with st.spinner("Running walk-forward validation..."):
            wfv = WalkForwardValidator(
                symbol          = symbol,
                start_date      = start_date,
                end_date        = end_date,
                n_training_days = int(n_days),
                interval        = "5m",
                fwd_bars        = int(fwd_bars),
                min_confidence  = float(min_confidence),
            )
            wf_result = wfv.run(progress_cb=_log)
            st.session_state["wf_result"] = wf_result

        progress_area.empty()

    wf = st.session_state.get("wf_result")
    if wf is None:
        st.info("Configure the walk-forward run above and click **▶ Run Walk-Forward**.")
        return

    st.success(
        f"**{symbol}** · {wf['n_days']} days evaluated · "
        f"{wf['n_errors']} errors"
    )

    # Aggregate summary
    st.subheader("Aggregate Summary — Static vs Adaptive")
    st.caption(
        "**⭐ Dir Accuracy (signal bars only)** is the primary trust metric — "
        "it measures accuracy only on bars where the model was confident enough to act. "
        "Signal Rate tells you how selective the model was."
    )

    metric_labels = {
        "avg_fidelity"         : "Avg Fidelity",
        "dir_accuracy"         : "Dir. Accuracy % (all bars)",
        "dir_accuracy_filtered": "⭐ Dir. Accuracy % (signal bars)",
        "signal_rate"          : "Signal Rate %",
        "mae"                  : "MAE %",
        "rmse"                 : "RMSE %",
        "sharpe_ratio"         : "Sharpe Ratio (signal bars)",
    }

    agg_rows = []
    for key, label in metric_labels.items():
        sv     = wf["summary_static"].get(key,           "—")
        sv_std = wf["summary_static"].get(f"{key}_std",  "—")
        av     = wf["summary_adaptive"].get(key,          "—")
        av_std = wf["summary_adaptive"].get(f"{key}_std", "—")
        dv     = wf["summary_delta"].get(f"delta_{key}",  "—")
        agg_rows.append({
            "Metric"             : label,
            "Static (mean±std)"  : f"{sv} ± {sv_std}" if sv != "—" else "—",
            "Adaptive (mean±std)": f"{av} ± {av_std}" if av != "—" else "—",
            "Δ mean"             : f"{dv:+.4f}" if isinstance(dv, float) else dv,
            "Adaptive wins?"     : "✅" if isinstance(dv, float) and dv > 0 else (
                                   "⚠️" if isinstance(dv, float) and dv < 0 else "—"),
        })

    st.dataframe(pd.DataFrame(agg_rows), use_container_width=True, hide_index=True)

    # Per-day table
    if not wf["per_day_df"].empty:
        st.subheader("Per-Day Results")
        # Prefer filtered accuracy columns; fall back to unfiltered
        show_cols = [
            "date", "prediction_bars",
            "static_dir_accuracy_filtered", "adaptive_dir_accuracy_filtered",
            "static_signal_rate",           "adaptive_signal_rate",
            "static_avg_fidelity",          "adaptive_avg_fidelity",
            "static_mae",                   "adaptive_mae",
            "delta_dir_accuracy_filtered",  "delta_avg_fidelity",
        ]
        show_cols = [c for c in show_cols if c in wf["per_day_df"].columns]
        st.dataframe(
            wf["per_day_df"][show_cols],
            use_container_width=True,
            hide_index=True,
        )

        # Filtered dir-accuracy delta over time
        if "delta_dir_accuracy_filtered" in wf["per_day_df"].columns:
            st.subheader("⭐ Δ Dir Accuracy Filtered (Adaptive − Static) per Day")
            ddf = wf["per_day_df"][["date", "delta_dir_accuracy_filtered"]].set_index("date")
            st.bar_chart(ddf["delta_dir_accuracy_filtered"], height=200)
            st.caption(
                "Positive = adaptive beats static on signal-bar accuracy that day. "
                "Values above 0 across most days = model has a real edge."
            )

        # Fidelity delta (secondary)
        elif "delta_avg_fidelity" in wf["per_day_df"].columns:
            st.subheader("Δ Fidelity (Adaptive − Static) per Day")
            delta_df = wf["per_day_df"][["date", "delta_avg_fidelity"]].set_index("date")
            st.bar_chart(delta_df["delta_avg_fidelity"], height=200)
            st.caption("Positive = adaptive outperforms static on that day.")

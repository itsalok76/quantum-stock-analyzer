"""
page_research_tracker.py

v6.2.0 — Actual vs Predicted Research Dashboard.

Features
--------
* Pick any NSE symbol + interval for the day.
* Runs the full QAMO v2 pipeline to generate a predicted close per bar.
* Prediction targets the bar 30 minutes ahead.
* The prediction line is plotted at the TARGET bar time — actual line at the
  same time — so both series share the same x-axis and are directly comparable.
* The "future" prediction stripe shows what the model is predicting RIGHT NOW
  for 30 min from now.
* Combined chart (Actual vs Predicted) + numerical comparison table.
* Auto-refresh: re-runs every N seconds while market is open.
* Directional accuracy, mean absolute error %, confidence shown as KPIs.

Version : 6.2.0
"""

from __future__ import annotations

import math
import time
import datetime

import streamlit as st
import pandas as pd

from live.qamo_engine_v2   import QAMOEngineV2
from live.research_tracker import ResearchTracker

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_INTERVAL_MINUTES: dict[str, int] = {
    "1m": 1, "2m": 2, "5m": 5, "10m": 10,
    "15m": 15, "30m": 30, "60m": 60, "1h": 60,
}


def _interval_mins(interval: str) -> int:
    return _INTERVAL_MINUTES.get(interval, 5)


def _fwd_bars(interval: str, target_minutes: int = 30) -> int:
    """Number of bars that equals 30 minutes for the chosen interval."""
    return max(1, math.ceil(target_minutes / _interval_mins(interval)))


# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------

def _get_engine(symbol: str, interval: str, n_bars: int) -> QAMOEngineV2:
    key = f"rt_engine_{symbol}_{interval}"
    if key not in st.session_state:
        st.session_state[key] = QAMOEngineV2(
            symbol=symbol, interval=interval, n_bars=n_bars,
        )
    return st.session_state[key]


def _get_tracker(symbol: str, interval: str, fwd: int) -> ResearchTracker:
    key = f"rt_tracker_{symbol}_{interval}"
    if key not in st.session_state:
        st.session_state[key] = ResearchTracker(capacity=500, fwd_bars=fwd)
    return st.session_state[key]


# ---------------------------------------------------------------------------
# Core one-cycle logic
# ---------------------------------------------------------------------------

def _run_cycle(engine: QAMOEngineV2, tracker: ResearchTracker, fwd: int) -> dict:
    """
    Run one QAMO-v2 refresh, feed every bar's actual price into tracker,
    and register a prediction aimed at the bar fwd*interval_mins from now.
    """
    result = engine.refresh()
    if "error" in result:
        return result

    bars = engine.buf.all()
    if not bars:
        return result

    # ── Record every bar in the buffer as "actual" ────────────────────
    # This ensures the Actual Close line is fully populated from the
    # very first refresh — not just the latest bar.
    for bar in bars:
        bar_ts = str(bar.timestamp)[:19]
        tracker.record_actual(
            bar_ts       = bar_ts,
            actual_close = bar.close,
            actual_open  = bar.open,
        )

    # ── Register this cycle's prediction ─────────────────────────────
    latest     = bars[-1]
    bar_ts     = str(latest.timestamp)[:19]
    exp_ret    = result.get("exp_return", 0.0)
    pred_close = round(latest.close * (1.0 + exp_ret / 100.0), 4)
    pred_p_up  = result.get("p_up", 0.5)
    pred_sig   = result.get("signal", "HOLD")
    pred_conf  = result.get("confidence_pct", 0.0) / 100.0

    mins_ahead = fwd * _interval_mins(engine.interval)
    try:
        from dateutil import parser as dtp
        base_dt   = dtp.parse(str(latest.timestamp))
        target_ts = (base_dt + datetime.timedelta(minutes=mins_ahead)
                     ).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        target_ts = bar_ts

    tracker.record_prediction(
        prediction_ts   = bar_ts,
        predicted_close = pred_close,
        signal          = pred_sig,
        exp_return      = exp_ret,
        confidence      = pred_conf,
        p_up            = pred_p_up,
        target_ts       = target_ts,
    )

    return result


# ---------------------------------------------------------------------------
# Chart builder  — returns one clean DataFrame ready for st.line_chart
# ---------------------------------------------------------------------------

def _build_combined_df(
    tracker  : ResearchTracker,
    bars_all : list,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns
    -------
    combined_df   : DataFrame indexed by datetime, columns:
                      "Actual Close"
                      "Predicted Close"        (resolved — same x as actual)
                      "Predicted +30 min"      (future — plotted ahead)
    resolved_df   : raw resolved records for the table
    """
    # ── Actual line — all bars in buffer ─────────────────────────────
    actual_rows = [
        {"ts": str(b.timestamp)[:19], "Actual Close": b.close}
        for b in bars_all
    ]
    actual_df = (
        pd.DataFrame(actual_rows)
        .drop_duplicates("ts")
        .sort_values("ts")
        .assign(ts=lambda d: pd.to_datetime(d["ts"]))
        .set_index("ts")
    )

    # ── Resolved predicted line ───────────────────────────────────────
    records = tracker.records()
    if records:
        resolved_df = pd.DataFrame([{
            "ts"          : r.timestamp,
            "actual"      : r.actual_close,
            "predicted"   : r.predicted_close,
            "signal"      : r.signal,
            "error_pct"   : r.error_pct,
            "correct_dir" : r.correct_dir,
            "p_up"        : r.p_up,
            "exp_return"  : r.exp_return,
            "confidence"  : r.confidence,
        } for r in records]).sort_values("ts")

        pred_df = (
            resolved_df[["ts", "predicted"]]
            .rename(columns={"predicted": "Predicted Close"})
            .assign(ts=lambda d: pd.to_datetime(d["ts"]))
            .set_index("ts")
        )
    else:
        resolved_df = pd.DataFrame()
        pred_df     = pd.DataFrame()

    # ── Future prediction line ────────────────────────────────────────
    pending = tracker.pending_predictions()
    if pending:
        future_rows = [
            {"ts": ts, "Predicted +30 min": p["predicted_close"]}
            for ts, p in pending.items()
        ]
        future_df = (
            pd.DataFrame(future_rows)
            .sort_values("ts")
            .assign(ts=lambda d: pd.to_datetime(d["ts"]))
            .set_index("ts")
        )
    else:
        future_df = pd.DataFrame()

    # ── Combine ───────────────────────────────────────────────────────
    combined = actual_df.copy()
    if not pred_df.empty:
        combined = combined.join(pred_df, how="outer")
    if not future_df.empty:
        combined = combined.join(future_df, how="outer")

    combined = combined.sort_index()
    return combined, resolved_df


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render(results: dict):

    st.title("📊 Research Tracker — Actual vs Predicted")
    st.caption(
        "v6.2.0 · Select a stock for the day · "
        "Prediction targets the next 30 min · "
        "Actual price lags prediction by 30 min on the chart"
    )
    st.divider()

    # ── Controls ─────────────────────────────────────────────────────
    col_sym, col_src, col_int, col_n, col_ref = st.columns([2, 2, 1, 1, 1])

    symbol = col_sym.text_input(
        "NSE Symbol",
        value=st.session_state.get("rt_last_symbol", "RELIANCE"),
        key="rt_symbol_input",
        help="Enter NSE ticker (without .NS)",
    ).strip().upper()

    col_src.selectbox(
        "Data Source",
        options=["Yahoo Finance"],
        index=0,
        help="Yahoo Finance works out of the box.",
    )

    interval = col_int.selectbox(
        "Interval",
        options=["5m", "1m", "15m", "30m"],   # 5m default — most reliable for Yahoo
        index=0,
        key="rt_interval_input",
    )

    n_bars = col_n.number_input(
        "History Bars",
        min_value=50,
        max_value=500,
        value=200,
        step=50,
        key="rt_nbars_input",
    )

    auto_refresh = col_ref.checkbox(
        "Auto-Refresh",
        value=False,
        help="Refresh every N seconds while market is open",
    )

    refresh_secs = 60
    if auto_refresh:
        refresh_secs = st.slider(
            "Refresh every (seconds)",
            min_value=15, max_value=300, value=60, step=15,
            key="rt_refresh_secs",
        )

    manual_refresh = st.button("🔄  Fetch / Refresh Now", type="primary")

    st.divider()

    # ── Day selector ─────────────────────────────────────────────────
    today         = datetime.date.today()
    selected_date = st.date_input(
        "Trading Day", value=today, max_value=today,
        help="Choose the day to monitor. Selecting today gives live data.",
        key="rt_date_input",
    )
    is_today = (selected_date == today)

    if not is_today:
        st.info(
            f"Selected past date **{selected_date}** — historical mode, "
            "no live refresh."
        )

    st.divider()

    # ── Reset tracker on symbol / interval change ─────────────────────
    fwd     = _fwd_bars(interval, target_minutes=30)
    engine  = _get_engine(symbol, interval, n_bars)
    tracker = _get_tracker(symbol, interval, fwd)

    prev_sym = st.session_state.get("rt_last_symbol")
    prev_int = st.session_state.get("rt_last_interval")
    if prev_sym != symbol or prev_int != interval:
        tracker.reset()
        # also drop cached engine so a fresh one is built
        eng_key = f"rt_engine_{symbol}_{interval}"
        if eng_key in st.session_state:
            del st.session_state[eng_key]
        engine = _get_engine(symbol, interval, n_bars)
        st.session_state["rt_last_symbol"]   = symbol
        st.session_state["rt_last_interval"] = interval

    # ── Decide whether to run ─────────────────────────────────────────
    skey        = f"rt_{symbol}_{interval}"
    last_ts_key = f"rt_last_ts_{symbol}_{interval}"
    last_run    = st.session_state.get(last_ts_key, 0.0)

    should_run = (
        manual_refresh
        or (skey not in st.session_state)
        or (auto_refresh and is_today and (time.time() - last_run) >= refresh_secs)
    )

    if should_run:
        with st.spinner(f"Running QAMO v2 for {symbol} ({interval})…"):
            cycle_result = _run_cycle(engine, tracker, fwd)
            st.session_state[skey]        = cycle_result
            st.session_state[last_ts_key] = time.time()

    cycle_result = st.session_state.get(skey, {})

    if "error" in cycle_result:
        st.error(cycle_result["error"])
        return

    bars_all = engine.buf.all()
    if not bars_all:
        st.warning(f"No data yet for {symbol}. Click 'Fetch / Refresh Now'.")
        return

    # ── Market status ─────────────────────────────────────────────────
    is_open = engine.is_market_open() if is_today else False
    s_col   = "#22c55e" if is_open else "#ef4444"
    s_txt   = "🟢 Market Open" if is_open else "🔴 Market Closed"

    latest  = bars_all[-1]
    prev_b  = bars_all[-2] if len(bars_all) > 1 else latest
    delta   = latest.close - prev_b.close
    pct     = delta / prev_b.close * 100 if prev_b.close else 0

    st.markdown(
        f"**{symbol}.NS** &nbsp;·&nbsp; {interval} &nbsp;·&nbsp; "
        f"Bars loaded: **{len(bars_all)}** &nbsp;·&nbsp; "
        f"Prediction horizon: **30 min ({fwd} bars)** &nbsp;·&nbsp; "
        f"<span style='color:{s_col};font-weight:700'>{s_txt}</span>",
        unsafe_allow_html=True,
    )

    # ── Price banner ──────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Close",  f"₹{latest.close:,.2f}", f"{delta:+.2f} ({pct:+.2f}%)")
    m2.metric("Open",   f"₹{latest.open:,.2f}")
    m3.metric("High",   f"₹{latest.high:,.2f}")
    m4.metric("Low",    f"₹{latest.low:,.2f}")
    m5.metric("Volume", f"{latest.volume:,.0f}")

    st.divider()

    # ── Research KPIs ─────────────────────────────────────────────────
    st.subheader("📐 Research Accuracy")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Resolved Pairs",       tracker.n_total)
    k2.metric("Directional Accuracy", f"{tracker.accuracy()*100:.1f}%")
    k3.metric("Mean Price Error %",   f"{tracker.mean_error_pct():.2f}%")
    k4.metric("QAMO Signal",          cycle_result.get("signal", "—"))
    k5.metric("Confidence",           f"{cycle_result.get('confidence_pct', 0):.1f}%")

    st.divider()

    # ── Chart ─────────────────────────────────────────────────────────
    st.subheader("📈 Actual vs Predicted — Price Chart")
    st.caption(
        "**Actual Close** = live/historical bars · "
        "**Predicted Close** = what the model forecast 30 min earlier for this bar · "
        "**Predicted +30 min** = what the model forecasts for the next 30 min"
    )

    combined_df, resolved_df = _build_combined_df(tracker, bars_all)

    if not combined_df.empty and len(combined_df) >= 2:
        st.line_chart(combined_df, height=400, width="stretch")
    else:
        # Show at least the raw price bars so the user sees something immediately
        raw_df = pd.DataFrame(
            [{"ts": pd.to_datetime(str(b.timestamp)[:19]), "Actual Close": b.close}
             for b in bars_all]
        ).drop_duplicates("ts").set_index("ts").sort_index()
        if not raw_df.empty:
            st.line_chart(raw_df, height=400, width="stretch")
        st.info(
            f"📌 **{len(bars_all)} bars loaded** — showing raw price above. "
            f"Predictions resolve after {fwd} bars "
            f"({fwd * _interval_mins(interval)} min). "
            "Keep refreshing and the Predicted line will appear."
        )

    # ── Numerical table ────────────────────────────────────────────────
    st.divider()
    st.subheader("🔢 Actual vs Predicted — Numerical Table")
    st.caption(
        f"Each row = one resolved pair. "
        f"Prediction was made {fwd} bars ({fwd * _interval_mins(interval)} min) earlier."
    )

    if not resolved_df.empty:
        disp = resolved_df[[
            "ts", "actual", "predicted",
            "error_pct", "correct_dir",
            "signal", "p_up", "exp_return", "confidence",
        ]].copy().sort_values("ts", ascending=False)

        disp.rename(columns={
            "ts"          : "Time",
            "actual"      : "Actual Close ₹",
            "predicted"   : "Predicted Close ₹",
            "error_pct"   : "Price Error %",
            "correct_dir" : "Direction ✓",
            "signal"      : "Signal",
            "p_up"        : "P(Up)",
            "exp_return"  : "Exp Return %",
            "confidence"  : "Confidence",
        }, inplace=True)

        disp["Actual Close ₹"]    = disp["Actual Close ₹"].map("₹{:,.2f}".format)
        disp["Predicted Close ₹"] = disp["Predicted Close ₹"].map("₹{:,.2f}".format)
        disp["Price Error %"]     = disp["Price Error %"].map("{:.3f}%".format)
        disp["P(Up)"]             = disp["P(Up)"].map("{:.3f}".format)
        disp["Exp Return %"]      = disp["Exp Return %"].map("{:+.3f}%".format)
        disp["Confidence"]        = disp["Confidence"].map("{:.3f}".format)
        disp["Direction ✓"]       = disp["Direction ✓"].map(lambda v: "✅" if v else "❌")

        st.dataframe(disp.head(60), width="stretch", hide_index=True)
        st.caption(f"Showing latest 60 of {len(resolved_df)} resolved pairs.")
    else:
        mins_needed = fwd * _interval_mins(interval)
        st.info(
            f"⏳ No resolved pairs yet — need {fwd} more refreshes "
            f"(≈ {mins_needed} min of market data). "
            "Keep clicking **Fetch / Refresh Now** or enable Auto-Refresh."
        )

    # ── Pending predictions ────────────────────────────────────────────
    pending = tracker.pending_predictions()
    with st.expander(
        f"⏳ Pending Predictions — {len(pending)} entries "
        f"(will resolve as bars arrive)"
    ):
        if pending:
            pend_rows = [
                {
                    "Target Time (approx)" : ts,
                    "Predicted Close"      : f"₹{p['predicted_close']:,.2f}",
                    "Signal"               : p["signal"],
                    "P(Up)"                : f"{p['p_up']:.3f}",
                    "Exp Return %"         : f"{p['exp_return']:+.3f}%",
                }
                for ts, p in sorted(pending.items())
            ]
            st.dataframe(
                pd.DataFrame(pend_rows), width="stretch", hide_index=True
            )
        else:
            st.info("No pending predictions.")

    # ── Auto-refresh via rerun ─────────────────────────────────────────
    if auto_refresh and is_today:
        elapsed   = time.time() - last_run
        remaining = max(0, int(refresh_secs - elapsed))
        if is_open:
            st.caption(
                f"🔄 Auto-refresh active · Next refresh in ~{remaining}s"
            )
            if elapsed >= refresh_secs:
                st.rerun()
            else:
                time.sleep(1)
                st.rerun()
        else:
            st.caption("⏸ Auto-refresh on — waiting for market to open.")

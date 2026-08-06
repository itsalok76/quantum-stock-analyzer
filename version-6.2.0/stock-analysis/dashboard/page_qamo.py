"""
page_qamo.py

Stage 13 — Research Dashboard (Full QAMO UI).

Single-screen live monitor layout:
    ┌─ Live Price + OHLCV ─────────────────────────────────┐
    ├─ Quantum State (qubit angles + P(|1>) per qubit) ────┤
    ├─ Fidelity / Velocity trend ──────────────────────────┤
    ├─ State Entropy ──────────────────────────────────────┤
    ├─ Similar Historical States (top-k table) ────────────┤
    ├─ AI Explanation (watsonx / fallback) ────────────────┤
    ├─ Prediction: Signal · Confidence · Stability · Risk  ┤
    ├─ Strategy Simulator (equity curve + metrics) ────────┤
    └─ Multi-window Feature Vector ────────────────────────┘

Version : 5.13.0
"""

from __future__ import annotations

import math
import numpy as np
import streamlit as st
import pandas as pd

from live.qamo_engine import QAMOEngine
from live.yahoo_feed  import YahooFeed

# Signal colour map
_SIG_COLOR = {"BUY": "#22c55e", "SELL": "#ef4444", "HOLD": "#f59e0b"}
_RISK_COLOR = {"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"}


# ------------------------------------------------------------------
# Helper: get or build QAMOEngine in session state
# ------------------------------------------------------------------

def _get_engine(symbol: str, interval: str, source: str) -> QAMOEngine:
    key = f"qamo_{symbol}_{interval}_{source}"
    if key not in st.session_state:
        feed = _make_feed(source, symbol, interval)
        st.session_state[key] = QAMOEngine(
            symbol   = symbol,
            interval = interval,
            feed     = feed,
            n_bars   = 200,
            load_db  = True,
        )
    return st.session_state[key]


def _make_feed(source: str, symbol: str, interval: str):
    if source == "Yahoo Finance":
        return YahooFeed(symbol, interval)
    elif source == "Zerodha Kite Connect":
        from live.zerodha_feed import ZerodhaFeed
        return ZerodhaFeed(symbol, interval)
    return YahooFeed(symbol, interval)


# ------------------------------------------------------------------
# Main render
# ------------------------------------------------------------------

def render(results: dict):

    st.title("⚛️ QAMO — Quantum Adaptive Market Observer")
    st.caption(
        "v5.13.0 · Stage 13 — Full Research Dashboard  |  "
        "14-stage quantum pipeline: Live Feed → Quantum State → Similarity → "
        "Prediction → Confidence → AI Explanation → Strategy"
    )

    st.divider()

    # Controls
    c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
    symbol   = c1.text_input("NSE Symbol", value="RELIANCE").strip().upper()
    source   = c2.selectbox("Source", ["Yahoo Finance", "Zerodha Kite Connect"])
    interval = c3.selectbox("Interval", ["1m", "5m", "15m", "30m"])
    n_bars   = c4.number_input("Bars", min_value=50, max_value=500, value=200, step=50)

    col_refresh, col_eval = st.columns([1, 1])
    refresh_btn = col_refresh.button("🔄  Refresh", type="primary", width="stretch")
    eval_btn    = col_eval.button("📊  Nightly Eval", width="stretch")

    st.divider()

    if source != "Yahoo Finance":
        st.info(f"**{source}** requires API credentials. See **📡 Live Monitor** for setup.")
        return

    engine = _get_engine(symbol, interval, source)
    engine.n_bars = n_bars

    # Nightly eval
    if eval_btn:
        with st.spinner("Running self-evaluation..."):
            report = engine.nightly_eval()
        st.success("Self-evaluation complete.")
        _render_eval(report)
        return

    # Refresh
    if refresh_btn or f"qamo_result_{symbol}" not in st.session_state:
        with st.spinner(f"Running QAMO pipeline for {symbol}..."):
            result = engine.refresh()
            st.session_state[f"qamo_result_{symbol}"]  = result
            st.session_state[f"qamo_engine_{symbol}"]  = engine

    result = st.session_state.get(f"qamo_result_{symbol}", {})
    engine = st.session_state.get(f"qamo_engine_{symbol}", engine)

    if "error" in result:
        st.error(result["error"])
        return

    fv    = engine.latest_fv or {}
    score = engine.latest_score or result
    state = engine.latest_state

    # ------------------------------------------------------------------
    # 1. Market status + price banner
    # ------------------------------------------------------------------
    is_open = engine.is_market_open()
    s_col   = "#22c55e" if is_open else "#ef4444"
    s_txt   = "🟢 Market Open" if is_open else "🔴 Market Closed"
    st.markdown(
        f"**{symbol}.NS** &nbsp;·&nbsp; Interval: **{interval}** &nbsp;·&nbsp; "
        f"Memory: **{len(engine.memory)}** states &nbsp;·&nbsp; "
        f"<span style='color:{s_col};font-weight:600'>{s_txt}</span>",
        unsafe_allow_html=True,
    )

    bars = engine.buf.all()
    if bars:
        latest = bars[-1]
        prev   = bars[-2] if len(bars) > 1 else latest
        delta  = latest.close - prev.close
        pct    = delta / prev.close * 100 if prev.close != 0 else 0

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Close",  f"₹{latest.close:,.2f}", f"{delta:+.2f} ({pct:+.2f}%)")
        m2.metric("Open",   f"₹{latest.open:,.2f}")
        m3.metric("High",   f"₹{latest.high:,.2f}")
        m4.metric("Low",    f"₹{latest.low:,.2f}")
        m5.metric("Volume", f"{latest.volume:,.0f}")
        m6.metric("VWAP",   f"₹{latest.vwap:,.2f}")

    st.divider()

    # ------------------------------------------------------------------
    # 2. Prediction signal banner
    # ------------------------------------------------------------------
    sig  = score.get("signal", "HOLD")
    scol = _SIG_COLOR.get(sig, "#888")
    rcol = _RISK_COLOR.get(score.get("risk", "Medium"), "#888")

    st.markdown(
        f"<div style='padding:12px 16px;border-radius:8px;"
        f"border:2px solid {scol};background:{scol}18;margin-bottom:8px'>"
        f"<span style='font-size:22px;font-weight:700;color:{scol}'>{sig}</span>"
        f"&nbsp;&nbsp;"
        f"P(Close>Open): <b>{score.get('p_up',0.5)*100:.1f}%</b> &nbsp;|&nbsp; "
        f"P(Open>Close): <b>{score.get('p_down',0.5)*100:.1f}%</b> &nbsp;|&nbsp; "
        f"Expected: <b>{score.get('exp_return',0):+.2f}%</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Confidence",   f"{score.get('confidence_pct', 0):.1f}%")
    sc2.metric("Stability",    f"{score.get('stability_pct',  0):.1f}%")
    sc3.metric("Risk",         score.get("risk", "—"))
    sc4.metric("Qvel Δψ",      f"{engine.velocity:.4f}")

    st.divider()

    # ------------------------------------------------------------------
    # 3. Quantum State — qubit table
    # ------------------------------------------------------------------
    st.subheader("⚛️ Quantum State |ψ(t)⟩  — 8-qubit register")
    if state:
        qrows = []
        for i, (lbl, ang) in enumerate(zip(state.LABELS, state.angles)):
            qrows.append({
                "Qubit": f"q{i}",
                "Feature"  : lbl,
                "Ry Angle" : f"{ang:.4f} rad",
                "P(|1>)"   : f"{state.qubit_p1(i):.4f}",
                "Bloch Z"  : f"{math.cos(ang):.4f}",
            })
        st.dataframe(pd.DataFrame(qrows), width="stretch", hide_index=True)

    # ------------------------------------------------------------------
    # 4. Fidelity / velocity trend
    # ------------------------------------------------------------------
    st.subheader("Fidelity & Velocity Trend")
    recs = engine.memory.records()
    if len(recs) >= 3:
        fids = []
        vels = []
        tss  = []
        for i in range(1, min(len(recs), 100)):
            psi1 = recs[-i - 1]["state"].statevector()
            psi2 = recs[-i  ]["state"].statevector()
            f    = float(abs(psi1.conj() @ psi2) ** 2)
            fids.append(f)
            vels.append(1.0 - f)
            tss.append(str(recs[-i]["timestamp"])[:19])

        fids.reverse(); vels.reverse(); tss.reverse()
        fv_df = pd.DataFrame({"Date": tss, "Fidelity": fids, "Velocity": vels})
        fv_df = fv_df.set_index("Date")
        col_f, col_v = st.columns(2)
        col_f.line_chart(fv_df["Fidelity"], height=180)
        col_f.caption("F(ψ_t, ψ_{t-1}) — near 1 = stable")
        col_v.line_chart(fv_df["Velocity"], height=180)
        col_v.caption("1 - F — state change rate")

    # ------------------------------------------------------------------
    # 5. State entropy
    # ------------------------------------------------------------------
    st.subheader("Quantum Entropy H(ψ_t)")
    if recs:
        ent_vals = []
        ent_ts   = []
        for rec in recs[-80:]:
            probs = rec["state"].probabilities()
            probs = probs[probs > 1e-12]
            h     = float(-np.sum(probs * np.log2(probs)))
            ent_vals.append(h)
            ent_ts.append(str(rec["timestamp"])[:19])
        ent_df = pd.DataFrame({"Date": ent_ts, "Entropy": ent_vals}).set_index("Date")
        st.line_chart(ent_df["Entropy"], height=160)
        st.caption("Low entropy → concentrated, stable state. High → uncertain market.")

    # ------------------------------------------------------------------
    # 6. Similar historical states
    # ------------------------------------------------------------------
    st.subheader("Similar Historical States (Top-k Matches)")
    matches = engine.latest_signal.get("matches", []) if engine.latest_signal else []
    if matches:
        mrows = [{
            "Rank"          : m["rank"],
            "Date"          : str(m["timestamp"])[:19],
            "Fidelity"      : f"{m['fidelity']:.4f}",
            "Green"         : "✅" if m["green"] else "🔴",
            "Next Green"    : ("✅" if m["next_green"] else "🔴") if m["next_green"] is not None else "—",
            "Next Δ%"       : f"{m['pct_change']:+.2f}%" if m["pct_change"] is not None else "—",
        } for m in matches[:10]]
        st.dataframe(pd.DataFrame(mrows), width="stretch", hide_index=True)
    else:
        st.info("Not enough memory for similarity search yet. Keep refreshing to build history.")

    # ------------------------------------------------------------------
    # 7. AI Explanation
    # ------------------------------------------------------------------
    st.subheader("🤖 AI Explanation (IBM watsonx / Fallback)")
    exp = engine.latest_explain or result.get("explanation", "")
    if exp:
        st.markdown(exp)
    else:
        st.info("Click Refresh to generate explanation.")

    # ------------------------------------------------------------------
    # 8. Strategy Simulator
    # ------------------------------------------------------------------
    st.subheader("📈 Strategy Simulator")
    sim_res = engine.simulator.results()
    if sim_res:
        sm1, sm2, sm3, sm4, sm5 = st.columns(5)
        sm1.metric("Total Return",  f"{sim_res['total_return_pct']:+.2f}%")
        sm2.metric("Sharpe Ratio",  f"{sim_res['sharpe_ratio']:.3f}")
        sm3.metric("Win Rate",      f"{sim_res['win_rate']:.1f}%")
        sm4.metric("Max Drawdown",  f"{sim_res['max_drawdown_pct']:.2f}%")
        sm5.metric("Sortino",       f"{sim_res['sortino_ratio']:.3f}")

        eq  = engine.simulator.equity_curve()
        if len(eq) > 1:
            eq_df = pd.DataFrame({"Equity": eq})
            st.line_chart(eq_df["Equity"], height=180)

    # ------------------------------------------------------------------
    # 9. Multi-window feature vector
    # ------------------------------------------------------------------
    with st.expander("Multi-Window Feature Vector"):
        if fv:
            from live.multi_window_features import WINDOWS, WINDOW_LABELS
            feat_names = ["return", "volatility", "rsi", "macd",
                          "momentum", "volume_spike", "vwap_dev"]
            wf_rows = []
            for wn, wlabel in WINDOW_LABELS.items():
                row = {"Window": f"{wn} ({wlabel})"}
                for fn in feat_names:
                    key = f"{fn}_{wn}"
                    row[fn] = round(fv.get(key, 0.0), 4)
                wf_rows.append(row)
            st.dataframe(pd.DataFrame(wf_rows), width="stretch", hide_index=True)

    # ------------------------------------------------------------------
    # 10. Online learner stats
    # ------------------------------------------------------------------
    with st.expander("Online Learning Stats"):
        learner = engine.learner
        lc1, lc2, lc3 = st.columns(3)
        lc1.metric("Total Predictions", learner.n_total)
        lc2.metric("Accuracy",          f"{learner.accuracy()*100:.1f}%")
        lc3.metric("Recent (last 20)",  f"{learner.recent_accuracy()*100:.1f}%")


# ------------------------------------------------------------------
# Nightly eval sub-render
# ------------------------------------------------------------------

def _render_eval(report: dict):
    st.subheader("📊 Nightly Self-Evaluation")
    if report.get("status") == "no_data":
        st.warning("No predictions recorded yet.")
        return
    ec1, ec2, ec3, ec4 = st.columns(4)
    ec1.metric("Predictions",   report.get("n_predictions", 0))
    ec2.metric("Dir. Accuracy", f"{report.get('directional_accuracy', 0):.1f}%")
    ec3.metric("Return MAE",    f"{report.get('return_mae', 0):.4f}%")
    ec4.metric("Retrain?",      "Yes ⚠️" if report.get("retrain_needed") else "No ✓")

    sim = report.get("strategy", {})
    if sim:
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Sharpe", sim.get("sharpe_ratio", "—"))
        sc2.metric("Drawdown", f"{sim.get('max_drawdown_pct','—')}%")
        sc3.metric("Total Return", f"{sim.get('total_return_pct','—')}%")

    st.subheader("Recommendations")
    for r in report.get("recommendations", []):
        st.markdown(f"• {r}")

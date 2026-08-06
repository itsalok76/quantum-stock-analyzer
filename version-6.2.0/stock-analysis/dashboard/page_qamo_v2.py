"""
page_qamo_v2.py

Stage 13 (v2) — Research Dashboard: Adaptive Quantum Market Observer.

New sections vs v1:
    - Qubit count timeline  (the market deciding its own circuit size)
    - Complexity score trend
    - Trajectory curvature chart
    - Circuit adaptation history (angle drift over time)
    - Predicted |ψ(t+1)⟩ qubit table
    - n_qubits breakdown by market condition

Version : 5.2.0
"""

from __future__ import annotations

import math
import numpy as np
import streamlit as st
import pandas as pd

from live.qamo_engine_v2 import QAMOEngineV2
from live.yahoo_feed     import YahooFeed

_SIG_COLOR  = {"BUY": "#22c55e", "SELL": "#ef4444", "HOLD": "#f59e0b"}
_RISK_COLOR = {"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"}


def _get_engine(symbol: str, interval: str) -> QAMOEngineV2:
    key = f"qamo_v2_{symbol}_{interval}"
    if key not in st.session_state:
        st.session_state[key] = QAMOEngineV2(
            symbol   = symbol,
            interval = interval,
            n_bars   = 200,
        )
    return st.session_state[key]


def render(results: dict):

    st.title("⚛️ QAMO v2 — Adaptive Quantum Market Observer")
    st.caption(
        "v5.2.0 · Self-evolving circuit · Dynamic qubit allocation (A+B) · "
        "Predict |ψ(t+1)⟩ · Real-time angle correction · No overnight retraining"
    )

    st.divider()

    c1, c2, c3 = st.columns([2, 1, 1])
    symbol   = c1.text_input("NSE Symbol", value="RELIANCE").strip().upper()
    interval = c2.selectbox("Interval", ["5m", "1m", "15m", "30m"])
    n_bars   = c3.number_input("Bars", min_value=50, max_value=500, value=200, step=50)

    refresh_btn = st.button("🔄  Refresh", type="primary", width="stretch")

    st.divider()

    engine = _get_engine(symbol, interval)
    engine.n_bars = n_bars

    if refresh_btn or f"qamo_v2_result_{symbol}" not in st.session_state:
        with st.spinner(f"Running QAMO v2 pipeline for {symbol}..."):
            result = engine.refresh()
            st.session_state[f"qamo_v2_result_{symbol}"] = result
            st.session_state[f"qamo_v2_engine_{symbol}"] = engine

    result = st.session_state.get(f"qamo_v2_result_{symbol}", {})
    engine = st.session_state.get(f"qamo_v2_engine_{symbol}", engine)

    if "error" in result:
        st.error(result["error"])
        return

    fv      = engine.latest_fv     or {}
    score   = engine.latest_score  or result
    state   = engine.latest_state
    traj    = engine.latest_traj   or {}
    comp    = engine.latest_complexity or {}
    pred    = engine.latest_prediction or {}
    alloc   = engine.allocator

    # ------------------------------------------------------------------
    # 1. Market status
    # ------------------------------------------------------------------
    is_open = engine.is_market_open()
    s_col   = "#22c55e" if is_open else "#ef4444"
    s_txt   = "🟢 Market Open" if is_open else "🔴 Market Closed"

    st.markdown(
        f"**{symbol}.NS** &nbsp;·&nbsp; {interval} &nbsp;·&nbsp; "
        f"Memory: **{len(engine.memory)}** states &nbsp;·&nbsp; "
        f"Circuit updates: **{engine.adaptor.n_updates}** &nbsp;·&nbsp; "
        f"<span style='color:{s_col};font-weight:600'>{s_txt}</span>",
        unsafe_allow_html=True,
    )

    bars = engine.buf.all()
    if bars:
        latest = bars[-1]
        prev   = bars[-2] if len(bars) > 1 else latest
        delta  = latest.close - prev.close
        pct    = delta / prev.close * 100 if prev.close != 0 else 0
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Close",  f"₹{latest.close:,.2f}", f"{delta:+.2f} ({pct:+.2f}%)")
        m2.metric("Open",   f"₹{latest.open:,.2f}")
        m3.metric("High",   f"₹{latest.high:,.2f}")
        m4.metric("Low",    f"₹{latest.low:,.2f}")
        m5.metric("VWAP",   f"₹{latest.vwap:,.2f}")

    st.divider()

    # ------------------------------------------------------------------
    # 2. Signal banner + qubit count (THE novel display)
    # ------------------------------------------------------------------
    sig  = score.get("signal", "HOLD")
    scol = _SIG_COLOR.get(sig, "#888")
    n_q  = alloc.current_n

    st.markdown(
        f"<div style='padding:12px 16px;border-radius:8px;"
        f"border:2px solid {scol};background:{scol}18;margin-bottom:8px'>"
        f"<span style='font-size:22px;font-weight:700;color:{scol}'>{sig}</span>"
        f"&nbsp;&nbsp;"
        f"P(Close>Open): <b>{score.get('p_up',0.5)*100:.1f}%</b> &nbsp;|&nbsp; "
        f"Expected: <b>{score.get('exp_return',0):+.2f}%</b> &nbsp;|&nbsp; "
        f"Circuit: <b>{n_q} qubits</b> (2^{n_q}={2**n_q} dims)"
        f"</div>",
        unsafe_allow_html=True,
    )

    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    sc1.metric("Confidence",   f"{score.get('confidence_pct', 0):.1f}%")
    sc2.metric("Stability",    f"{score.get('stability_pct',  0):.1f}%")
    sc3.metric("Risk",         score.get("risk", "—"))
    sc4.metric("Complexity C(t)", f"{comp.get('complexity', 0):.3f}")
    sc5.metric("Qubits n(t)", f"{n_q}  ({alloc._delta:+d} correction)")

    st.divider()

    # ------------------------------------------------------------------
    # 3. Qubit count timeline — THE novel chart
    # ------------------------------------------------------------------
    st.subheader("⚛️ Dynamic Qubit Allocation — n(t)")
    st.caption(
        "The market decides the circuit size. "
        "Flat market → 3 qubits. Volatile/chaotic → up to 12 qubits."
    )
    q_hist = alloc.qubit_trajectory()
    c_hist = alloc.complexity_trajectory()
    if len(q_hist) > 1:
        ts_hist = [h["timestamp"][:19] for h in alloc.history[-len(q_hist):]]
        qdf = pd.DataFrame({
            "Time"       : ts_hist[-100:],
            "n_qubits"   : q_hist[-100:],
            "complexity" : c_hist[-100:],
        }).set_index("Time")
        col_q, col_c = st.columns(2)
        col_q.line_chart(qdf["n_qubits"],   height=200, width="stretch")
        col_q.caption("n_qubits(t) — market-driven circuit complexity")
        col_c.line_chart(qdf["complexity"], height=200, width="stretch")
        col_c.caption("Complexity C(t) — entropy + PCA rank + decorrelation")

        # Qubit distribution pie (as bar chart)
        from collections import Counter
        counts = Counter(q_hist)
        dist_df = pd.DataFrame({
            "n_qubits": list(counts.keys()),
            "count"   : list(counts.values()),
        }).sort_values("n_qubits")
        with st.expander("Qubit count distribution"):
            st.bar_chart(dist_df.set_index("n_qubits")["count"])
            st.caption("How often each qubit count was used — reflects market regime distribution.")

    st.divider()

    # ------------------------------------------------------------------
    # 4. Current quantum state — qubit table
    # ------------------------------------------------------------------
    st.subheader(f"⚛️ Current State |ψ(t)⟩  —  {n_q} qubits")
    if state:
        qrows = []
        for i, (lbl, ang) in enumerate(zip(state.labels, state.angles)):
            qrows.append({
                "q"      : f"q{i}",
                "Feature": lbl,
                "θ (rad)": f"{ang:.4f}",
                "P(|1⟩)" : f"{state.qubit_p1(i):.4f}",
                "Bloch Z": f"{math.cos(ang):.4f}",
            })
        st.dataframe(pd.DataFrame(qrows), width="stretch", hide_index=True)

    # ------------------------------------------------------------------
    # 5. Predicted next state |ψ(t+1)⟩
    # ------------------------------------------------------------------
    st.subheader("⚛️ Predicted Next State |ψ(t+1)⟩")
    pred_state = pred.get("predicted_state")
    if pred_state:
        prows = []
        for i, (lbl, ang) in enumerate(zip(pred_state.labels, pred_state.angles)):
            prows.append({
                "q"       : f"q{i}",
                "Feature" : lbl,
                "θ (rad)" : f"{ang:.4f}",
                "P(|1⟩)"  : f"{pred_state.qubit_p1(i):.4f}",
            })
        st.dataframe(pd.DataFrame(prows), width="stretch", hide_index=True)
        st.caption(
            f"Predicted state has {pred_state.n_qubits} qubits. "
            "All signals (P(up), risk, confidence) are derived from this state — "
            "price is one observable, not the target."
        )
    else:
        st.info("Predicted state not yet available — keep refreshing to build memory.")

    st.divider()

    # ------------------------------------------------------------------
    # 6. Trajectory: velocity + acceleration + curvature
    # ------------------------------------------------------------------
    st.subheader("Quantum Trajectory — Velocity · Acceleration · Curvature")
    if traj.get("velocities"):
        ts = traj["timestamps"][1:]   # aligned to velocities
        ncols = 3
        col_v, col_a, col_c2 = st.columns(ncols)

        if traj["velocities"]:
            vdf = pd.DataFrame({"Velocity": traj["velocities"][-80:]},
                               index=ts[-80:] if ts else None)
            col_v.line_chart(vdf, height=160)
            col_v.caption("dψ/dt — state change rate")

        if traj["accelerations"]:
            adf = pd.DataFrame({"Acceleration": traj["accelerations"][-80:]})
            col_a.line_chart(adf, height=160)
            col_a.caption("d²ψ/dt²")

        if traj["curvatures"]:
            cdf = pd.DataFrame({"Curvature": traj["curvatures"][-80:]})
            col_c2.line_chart(cdf, height=160)
            col_c2.caption("d³ψ/dt³ — trajectory bending")

    # ------------------------------------------------------------------
    # 7. Entropy timeline
    # ------------------------------------------------------------------
    st.subheader("State Entropy H(ψ_t)")
    if traj.get("entropies"):
        edf = pd.DataFrame({"Entropy": traj["entropies"][-80:]})
        st.line_chart(edf, height=160)
        st.caption("Low entropy → stable, concentrated state. High → uncertain.")

    # ------------------------------------------------------------------
    # 8. Circuit adaptation (angle drift)
    # ------------------------------------------------------------------
    st.subheader("🔧 Circuit Adaptation — Learned Angle Offsets")
    offsets = engine.encoder.offsets
    if offsets:
        odf = pd.DataFrame([
            {"Feature": k, "Angle Offset (rad)": round(v, 6)}
            for k, v in offsets.items()
        ])
        st.dataframe(odf, width="stretch", hide_index=True)
        st.caption(
            f"Adaptor updates: {engine.adaptor.n_updates} &nbsp;|&nbsp; "
            f"Mean error: {engine.adaptor.mean_error():.4f} &nbsp;|&nbsp; "
            f"Recent error (last 10): {engine.adaptor.recent_error():.4f}"
        )
    else:
        st.info("No angle corrections yet — circuit adapts after first prediction cycle.")

    # ------------------------------------------------------------------
    # 9. Similar historical states
    # ------------------------------------------------------------------
    st.subheader("Similar Historical States")
    matches = pred.get("matches", [])
    if matches:
        mrows = [{
            "Rank"     : m["rank"],
            "Date"     : str(m["timestamp"])[:19],
            "Fidelity" : f"{m['fidelity']:.4f}",
            "n_qubits" : m.get("n_qubits", "—"),
            "Complexity": m.get("complexity", "—"),
            "Green"    : "✅" if m["green"] else "🔴",
            "Next Green": ("✅" if m["next_green"] else "🔴")
                           if m["next_green"] is not None else "—",
            "Next Δ%"  : f"{m['pct_change']:+.2f}%"
                          if m["pct_change"] is not None else "—",
        } for m in matches[:10]]
        st.dataframe(pd.DataFrame(mrows), width="stretch", hide_index=True)
        st.caption(
            "Note: matches may have different n_qubits — cross-dimensional "
            "fidelity computed via state-vector padding."
        )
    else:
        st.info("Building memory… keep refreshing.")

    # ------------------------------------------------------------------
    # 10. AI explanation
    # ------------------------------------------------------------------
    st.subheader("🤖 AI Explanation")
    if engine.latest_explain:
        st.markdown(engine.latest_explain)

    # ------------------------------------------------------------------
    # 11. Strategy + online learning
    # ------------------------------------------------------------------
    sim_res = engine.simulator.results()
    if sim_res:
        st.subheader("📈 Strategy Performance")
        sm1, sm2, sm3, sm4 = st.columns(4)
        sm1.metric("Total Return",  f"{sim_res['total_return_pct']:+.2f}%")
        sm2.metric("Sharpe",        f"{sim_res['sharpe_ratio']:.3f}")
        sm3.metric("Win Rate",      f"{sim_res['win_rate']:.1f}%")
        sm4.metric("Max Drawdown",  f"{sim_res['max_drawdown_pct']:.2f}%")

    with st.expander("Multi-Window Feature Vector"):
        if fv:
            from live.multi_window_features import WINDOW_LABELS
            feats = ["return", "volatility", "rsi", "macd", "momentum", "volume_spike"]
            wrows = []
            for wn, wl in WINDOW_LABELS.items():
                row = {"Window": f"{wn} ({wl})"}
                for fn in feats:
                    row[fn] = round(fv.get(f"{fn}_{wn}", 0.0), 4)
                wrows.append(row)
            st.dataframe(pd.DataFrame(wrows), width="stretch", hide_index=True)

    with st.expander("Complexity Estimator Detail"):
        if comp:
            crows = [{"Metric": k, "Value": v} for k, v in comp.items()]
            st.dataframe(pd.DataFrame(crows), width="stretch", hide_index=True)

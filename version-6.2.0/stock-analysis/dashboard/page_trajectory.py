"""
page_trajectory.py

Streamlit page — Quantum State Trajectory (v4.1.0)

Displays:
    1. Quantum state evolution (fidelity over time)
    2. Velocity & acceleration time-series
    3. Regime timeline (colour-coded)
    4. Top-k nearest-neighbour matches
    5. Next-state forecast: P(Close>Open), P(Open>Close), expected return, confidence
    6. Walk-forward accuracy

Version : 4.1.0
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

# Regime colour map
REGIME_COLORS = {
    "Stable"   : "#3b82d4",
    "Reversal" : "#f59e0b",
    "Breakout" : "#22c55e",
    "Shock"    : "#ef4444",
}


def render(results: dict):

    st.title("⚛️ Quantum State Trajectory")
    st.caption(
        "v4.1.0 — Each trading day is encoded as a quantum state |ψ_t⟩. "
        "The model tracks how the state evolves, detects regime changes, "
        "and predicts the next state using fidelity-based similarity search."
    )

    traj_port = results.get("traj_portfolio")
    if traj_port is None:
        st.warning("Trajectory data not available. Please re-run analysis.")
        return

    symbols = traj_port.get_symbols()
    if not symbols:
        st.info("No trajectory results found.")
        return

    symbol = st.selectbox("Select stock", symbols)
    res    = traj_port.get_result(symbol)

    if "error" in res:
        st.error(res["error"])
        return

    traj     = res["trajectory"]
    vel      = res["velocity"]
    reg      = res["regime"]
    forecast = res["forecast"]
    learner  = res["learner"]

    # ------------------------------------------------------------------
    # Section 1 — Forecast banner
    # ------------------------------------------------------------------
    st.subheader("Next-Day Forecast")

    col1, col2, col3, col4 = st.columns(4)

    regime      = reg.latest_regime()
    regime_col  = REGIME_COLORS.get(regime, "#888")

    col1.metric("P(Close > Open)", f"{forecast['p_up']*100:.1f}%")
    col2.metric("P(Open > Close)", f"{forecast['p_down']*100:.1f}%")
    col3.metric("Expected Return", f"{forecast['exp_return']:+.2f}%")
    col4.metric("Confidence",      f"{forecast['confidence']:.3f}")

    st.markdown(
        f"**Current Regime:** "
        f"<span style='color:{regime_col}; font-weight:bold'>{regime}</span> &nbsp;|&nbsp; "
        f"Entropy: **{reg.latest_entropy():.3f}** &nbsp;|&nbsp; "
        f"Purity: **{reg.latest_purity():.3f}**",
        unsafe_allow_html=True,
    )

    st.divider()

    # ------------------------------------------------------------------
    # Section 2 — Fidelity over time (state evolution)
    # ------------------------------------------------------------------
    st.subheader("Quantum State Evolution — Fidelity F(ψ_t, ψ_{t-1})")

    if vel.fidelities:
        fid_df = pd.DataFrame({
            "Date"    : [str(d)[:10] for d in vel.dates_v],
            "Fidelity": vel.fidelities,
        })
        st.line_chart(fid_df.set_index("Date")["Fidelity"], height=220)
        st.caption(
            "Fidelity near 1.0 → state unchanged (stable market). "
            "Sharp drops signal regime transitions."
        )
    else:
        st.info("Insufficient data to plot fidelity.")

    # ------------------------------------------------------------------
    # Section 3 — Velocity & acceleration
    # ------------------------------------------------------------------
    st.subheader("Quantum Velocity  &  Acceleration")

    col_v, col_a = st.columns(2)

    if vel.velocities:
        v_df = pd.DataFrame({
            "Date"    : [str(d)[:10] for d in vel.dates_v],
            "Velocity": vel.velocities,
        })
        col_v.line_chart(v_df.set_index("Date")["Velocity"], height=200)
        col_v.caption("Δψ/Δt — state change per trading day")

    if vel.accelerations:
        a_df = pd.DataFrame({
            "Date"        : [str(d)[:10] for d in vel.dates_a],
            "Acceleration": vel.accelerations,
        })
        col_a.line_chart(a_df.set_index("Date")["Acceleration"], height=200)
        col_a.caption("d²ψ/dt² — rate of change of velocity")

    # ------------------------------------------------------------------
    # Section 4 — Regime timeline
    # ------------------------------------------------------------------
    st.subheader("Regime Timeline")

    if reg.regimes:
        reg_df = pd.DataFrame({
            "Date"   : [str(d)[:10] for d in reg.dates],
            "Regime" : reg.regimes,
        })

        counts = reg.regime_counts()
        rc1, rc2, rc3, rc4 = st.columns(4)
        for col, (label, color) in zip(
            [rc1, rc2, rc3, rc4],
            REGIME_COLORS.items()
        ):
            col.metric(label, counts.get(label, 0))

        st.dataframe(
            reg_df.tail(30).sort_index(ascending=False),
            width="stretch",
            hide_index=True,
        )
        st.caption("Showing last 30 days. Stable=slow market, Reversal=momentum turning, "
                   "Breakout=momentum building, Shock=sudden shift.")

    # ------------------------------------------------------------------
    # Section 5 — Entropy time-series
    # ------------------------------------------------------------------
    st.subheader("State Entropy H(ψ_t)")

    if reg.entropies:
        ent_dates = [str(d)[:10] for d in traj.dates]
        ent_df    = pd.DataFrame({
            "Date"   : ent_dates,
            "Entropy": reg.entropies,
        })
        st.line_chart(ent_df.set_index("Date")["Entropy"], height=200)
        st.caption(
            "Low entropy → stable, concentrated state. "
            "High entropy → chaotic, uncertain market."
        )

    # ------------------------------------------------------------------
    # Section 6 — Nearest-neighbour matches
    # ------------------------------------------------------------------
    st.subheader("Top-k Historical Matches (Nearest Neighbours)")

    matches = forecast.get("matches", [])
    if matches:
        rows = []
        for m in matches:
            rows.append({
                "Rank"            : m["rank"],
                "Date"            : str(m["date"])[:10],
                "Fidelity"        : f"{m['fidelity']:.4f}",
                "Day Green"       : "✅" if m["green"]      else "🔴",
                "Next Day Green"  : "✅" if m["next_green"] else ("🔴" if m["next_green"] is not None else "—"),
                "Next % Change"   : f"{m['pct_change']:+.2f}%" if m["pct_change"] is not None else "—",
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        st.caption(
            "States from history most similar to today's |ψ_now⟩ by fidelity. "
            "'Next Day' shows what actually happened after each historical match."
        )
    else:
        st.info("Not enough history for similarity search.")

    # ------------------------------------------------------------------
    # Section 7 — Walk-forward accuracy
    # ------------------------------------------------------------------
    st.subheader("Walk-Forward Learning Accuracy")

    acc_col1, acc_col2, acc_col3 = st.columns(3)
    acc_col1.metric("Accuracy",   f"{learner.accuracy()*100:.1f}%")
    acc_col2.metric("Correct",    learner.n_correct)
    acc_col3.metric("Total Preds", learner.n_total)

    st.caption(
        "Walk-forward: model trained on first 80% of history, "
        "scored day-by-day on the remaining 20%. "
        "Weights and thresholds updated after each prediction."
    )

    # Learned weights table
    with st.expander("Learned Encoder Weights & Thresholds"):
        w_df = pd.DataFrame([
            {"Parameter": k, "Value": round(v, 4)}
            for k, v in {**learner.weights, **learner.thresholds}.items()
        ])
        st.dataframe(w_df, width="stretch", hide_index=True)

"""
page_live_monitor.py

Streamlit page — Live Market Monitor (v5.1.0 / Stage 1)

Single-stock intraday quantum state monitor.

Features:
    - Pick any NSE symbol + data source + interval
    - Fetch latest bars on demand (Refresh button)
    - Display live price, feature vector, OHLCV table
    - Market status (open / closed)
    - Groundwork for Stage 2 quantum encoding (feature vector displayed)

Version : 5.1.0
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from live.yahoo_feed       import YahooFeed
from live.tick_buffer      import TickBuffer
from live.feature_generator import FeatureGenerator


# ------------------------------------------------------------------
# Source factory
# ------------------------------------------------------------------

def _make_feed(source: str, symbol: str, interval: str):
    if source == "Yahoo Finance":
        return YahooFeed(symbol, interval)
    elif source == "Zerodha Kite Connect":
        from live.zerodha_feed import ZerodhaFeed
        return ZerodhaFeed(symbol, interval)
    elif source == "Polygon.io":
        from live.polygon_feed import PolygonFeed
        return PolygonFeed(symbol, interval)
    elif source == "Alpaca":
        from live.alpaca_feed import AlpacaFeed
        return AlpacaFeed(symbol, interval)
    return YahooFeed(symbol, interval)


# ------------------------------------------------------------------
# Main render
# ------------------------------------------------------------------

def render(results: dict):

    st.title("📡 Live Market Monitor")
    st.caption(
        "v5.1.0 · Stage 1 — Live Market Data Acquisition  |  "
        "Single-stock intraday feed → Tick Buffer → Feature Vector"
    )

    st.divider()

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------
    col_sym, col_src, col_int, col_n = st.columns([2, 2, 1, 1])

    symbol = col_sym.text_input(
        "NSE Symbol",
        value="RELIANCE",
        help="Enter a single NSE ticker (without .NS)",
    ).strip().upper()

    source = col_src.selectbox(
        "Data Source",
        options=[
            "Yahoo Finance",
            "Zerodha Kite Connect",
            "Polygon.io",
            "Alpaca",
        ],
        index=0,
        help="Yahoo Finance works out of the box. Others require API keys.",
    )

    interval = col_int.selectbox(
        "Interval",
        options=["1m", "5m", "15m", "30m", "1h"],
        index=0,
    )

    n_bars = col_n.number_input(
        "Bars",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
    )

    refresh_btn = st.button("🔄  Refresh Data", type="primary")

    st.divider()

    # ------------------------------------------------------------------
    # Source setup note
    # ------------------------------------------------------------------
    if source != "Yahoo Finance":
        _show_setup_note(source)
        return

    # ------------------------------------------------------------------
    # Fetch
    # ------------------------------------------------------------------
    if refresh_btn or "live_bars" not in st.session_state or \
            st.session_state.get("live_symbol") != symbol or \
            st.session_state.get("live_interval") != interval:

        with st.spinner(f"Fetching {symbol} ({interval}) from {source}..."):
            try:
                feed   = _make_feed(source, symbol, interval)
                bars   = feed.fetch_latest(n_bars=n_bars)
                buf    = TickBuffer(capacity=1000)
                buf.extend(bars)
                st.session_state["live_bars"]     = bars
                st.session_state["live_buf"]      = buf
                st.session_state["live_symbol"]   = symbol
                st.session_state["live_interval"] = interval
                st.session_state["live_source"]   = source
                st.session_state["live_feed"]     = feed
            except Exception as ex:
                st.error(f"Data fetch failed: {ex}")
                return

    bars = st.session_state.get("live_bars", [])
    buf  = st.session_state.get("live_buf")
    feed = st.session_state.get("live_feed")

    if not bars:
        st.warning(f"No data returned for {symbol} at {interval} interval.")
        return

    # ------------------------------------------------------------------
    # Market status
    # ------------------------------------------------------------------
    is_open = feed.is_market_open() if feed else False
    status_col = "#22c55e" if is_open else "#ef4444"
    status_txt = "🟢 Market Open" if is_open else "🔴 Market Closed"

    st.markdown(
        f"**{source}** &nbsp;·&nbsp; "
        f"**{symbol}.NS** &nbsp;·&nbsp; "
        f"Interval: **{interval}** &nbsp;·&nbsp; "
        f"Bars loaded: **{len(bars)}** &nbsp;·&nbsp; "
        f"<span style='color:{status_col}; font-weight:600'>{status_txt}</span>",
        unsafe_allow_html=True,
    )

    latest = bars[-1]

    # ------------------------------------------------------------------
    # Price banner
    # ------------------------------------------------------------------
    price_change = round(latest.close - bars[-2].close, 4) \
                   if len(bars) > 1 else 0.0
    pct_change   = round(price_change / bars[-2].close * 100, 2) \
                   if len(bars) > 1 and bars[-2].close != 0 else 0.0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Price (Close)",  f"₹{latest.close:,.2f}",
              delta=f"{price_change:+.2f} ({pct_change:+.2f}%)")
    m2.metric("Open",   f"₹{latest.open:,.2f}")
    m3.metric("High",   f"₹{latest.high:,.2f}")
    m4.metric("Low",    f"₹{latest.low:,.2f}")
    m5.metric("Volume", f"{latest.volume:,.0f}")

    # ------------------------------------------------------------------
    # Feature Vector(t)
    # ------------------------------------------------------------------
    st.subheader("Feature Vector(t)")
    st.caption(
        "Stage 2 preview — intraday features computed from tick buffer. "
        "These will be encoded into |ψ(t)⟩ in v5.2 / v5.3."
    )

    fg = FeatureGenerator(buf)
    fv = fg.compute()

    if fv:
        fv_display = {
            "Price"           : f"₹{fv['price']:,.4f}",
            "Return %"        : f"{fv['return_pct']:+.4f}%",
            "Volatility"      : f"{fv['volatility']:.6f}",
            "VWAP"            : f"₹{fv['vwap']:,.4f}",
            "VWAP Deviation"  : f"{fv['vwap_dev']:+.4f}%",
            "RSI(14)"         : f"{fv['rsi']:.2f}",
            "EMA Fast(9)"     : f"₹{fv['ema_fast']:,.4f}",
            "EMA Slow(21)"    : f"₹{fv['ema_slow']:,.4f}",
            "MACD"            : f"{fv['macd']:+.6f}",
            "ATR(14)"         : f"{fv['atr']:.4f}",
            "Momentum"        : f"{fv['momentum']:+.4f}",
            "Volume"          : f"{fv['volume']:,.0f}",
            "Volume Spike"    : f"{fv['volume_spike']:.4f}x",
            "Spread"          : f"{fv['spread']:.4f}",
            "Order Imbalance" : f"{fv['order_imbalance']:+.6f}",
        }

        fv_half = len(fv_display) // 2
        items   = list(fv_display.items())
        fc1, fc2 = st.columns(2)

        with fc1:
            for k, v in items[:fv_half]:
                st.markdown(f"**{k}** &nbsp; `{v}`")
        with fc2:
            for k, v in items[fv_half:]:
                st.markdown(f"**{k}** &nbsp; `{v}`")
    else:
        st.info("Not enough bars to compute feature vector.")

    # ------------------------------------------------------------------
    # Price chart
    # ------------------------------------------------------------------
    st.subheader("Price (Close)")
    df = buf.to_dataframe()
    if not df.empty and "close" in df.columns:
        chart_df = df[["timestamp", "close"]].copy()
        chart_df["timestamp"] = chart_df["timestamp"].astype(str).str[:19]
        chart_df = chart_df.set_index("timestamp")
        st.line_chart(chart_df["close"], height=220)

    # ------------------------------------------------------------------
    # Volume chart
    # ------------------------------------------------------------------
    st.subheader("Volume")
    if not df.empty and "volume" in df.columns:
        vol_df = df[["timestamp", "volume"]].copy()
        vol_df["timestamp"] = vol_df["timestamp"].astype(str).str[:19]
        vol_df = vol_df.set_index("timestamp")
        st.bar_chart(vol_df["volume"], height=160)

    # ------------------------------------------------------------------
    # Feature history
    # ------------------------------------------------------------------
    st.subheader("Feature History")
    fv_df = fg.compute_dataframe()
    if not fv_df.empty:
        cols_to_show = [
            "timestamp", "price", "return_pct", "volatility",
            "rsi", "macd", "volume_spike", "vwap_dev",
        ]
        cols_present = [c for c in cols_to_show if c in fv_df.columns]
        st.dataframe(
            fv_df[cols_present].tail(30).sort_index(ascending=False),
            use_container_width=True,
            hide_index=True,
        )
        st.caption("Showing last 30 bars of computed features.")

    # ------------------------------------------------------------------
    # Raw OHLCV table
    # ------------------------------------------------------------------
    with st.expander("Raw OHLCV Data"):
        if not df.empty:
            show_cols = [c for c in
                         ["timestamp","open","high","low","close","volume","vwap"]
                         if c in df.columns]
            st.dataframe(
                df[show_cols].tail(50).sort_index(ascending=False),
                use_container_width=True,
                hide_index=True,
            )


# ------------------------------------------------------------------
# Setup notes for non-Yahoo sources
# ------------------------------------------------------------------

_SETUP_NOTES = {
    "Zerodha Kite Connect": """
**Zerodha Kite Connect Setup**

1. Sign up at [kite.trade](https://kite.trade/) and create an app
2. Install the SDK:
   ```
   pip install kiteconnect
   ```
3. Set environment variables before launching Streamlit:
   ```bash
   export KITE_API_KEY=your_api_key
   export KITE_ACCESS_TOKEN=your_access_token
   ```
4. Access token must be refreshed daily via the Kite login flow
5. Switch back to this page — it will connect automatically
""",
    "Polygon.io": """
**Polygon.io Setup**

1. Sign up at [polygon.io](https://polygon.io/)
2. Install the client:
   ```
   pip install polygon-api-client
   ```
3. Set environment variable:
   ```bash
   export POLYGON_API_KEY=your_api_key
   ```
> Note: Polygon primarily covers US equities. For NSE stocks, use Yahoo Finance or Zerodha.
""",
    "Alpaca": """
**Alpaca Setup**

1. Sign up at [alpaca.markets](https://alpaca.markets/)
2. Install the SDK:
   ```
   pip install alpaca-py
   ```
3. Set environment variables:
   ```bash
   export ALPACA_API_KEY=your_api_key
   export ALPACA_SECRET_KEY=your_secret_key
   ```
> Note: Alpaca covers US equities. For NSE stocks, use Yahoo Finance or Zerodha.
""",
}


def _show_setup_note(source: str):
    note = _SETUP_NOTES.get(source, "")
    if note:
        st.info(f"**{source}** requires setup. Instructions below.")
        st.markdown(note)

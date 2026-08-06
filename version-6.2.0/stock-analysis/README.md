# QAMO — Quantum Adaptive Market Observer

**Version 5.3.0** — Quantum Trajectory Experiment Engine

A Python + Qiskit + Streamlit framework that combines classical financial
analytics with quantum computing to analyse NSE stocks.  
The system encodes intraday market features into quantum states, runs a
self-evolving qubit circuit whose size is decided by the market's own
complexity, tracks state evolution over time, and benchmarks static vs
adaptive prediction — all inside an interactive web dashboard.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Virtual Environment Setup](#virtual-environment-setup)
3. [Installation](#installation)
4. [Running the Dashboard](#running-the-dashboard)
5. [Running the CLI](#running-the-cli)
6. [Dashboard Pages](#dashboard-pages)
7. [Project Structure](#project-structure)
8. [Pipeline — Step by Step](#pipeline--step-by-step)
9. [Reading the Output](#reading-the-output)
10. [Quantum Modules](#quantum-modules)
11. [Output Files](#output-files)
12. [IBM watsonx AI (Optional)](#ibm-watsonx-ai-optional)
13. [Version History](#version-history)
14. [Disclaimer](#disclaimer)

---

## Requirements

| Package | Minimum Version | Purpose |
|---------|----------------|---------|
| Python | 3.10+ | Runtime |
| yfinance | 1.5.0 | NSE historical data (Yahoo Finance) |
| pandas | 2.3.0 | DataFrames and time series |
| numpy | 2.5.0 | Numerical computation |
| matplotlib | 3.11.0 | Price, return and volume charts |
| scipy | 1.18.0 | VQC optimiser (COBYLA) |
| plotly | 6.9.0 | Interactive correlation heatmaps |
| tabulate | 0.10.0 | Console table formatting |
| colorama | 0.4.6 | Coloured terminal output |
| ibm-watsonx-ai | 1.6.0 | IBM Granite AI report (optional) |
| qiskit | 2.5.0 | Quantum circuit construction |
| qiskit-aer | 0.17.0 | Quantum circuit simulation (Aer) |
| streamlit | 1.59.0 | Interactive web dashboard |
| kiteconnect | 5.0.0 | Zerodha Kite Connect live feed (optional) |
| pyarrow | 14.0.0 | Parquet persistence for quantum state DB |

All dependencies are listed in `requirements.txt`.

---

## Virtual Environment Setup

### macOS / Linux

```bash
# 1. Create the virtual environment
python3 -m venv my_env

# 2. Activate it
source my_env/bin/activate

# 3. Confirm activation (prompt should show (my_env))
which python
```

### Windows

```bash
# 1. Create the virtual environment
python -m venv my_env

# 2. Activate it
my_env\Scripts\activate

# 3. Confirm activation
where python
```

### Deactivate when done

```bash
deactivate
```

---

## Installation

```bash
# With the virtual environment active:
pip install -r requirements.txt
```

> **Qiskit note:** `qiskit-aer` requires a C++ compiler on some systems.
> On macOS run `xcode-select --install` if the install fails.
> On Ubuntu run `sudo apt install build-essential`.

---

## Running the Dashboard

The dashboard is the primary interface. No command-line arguments are needed —
everything is configured through the sidebar.

```bash
# With the virtual environment active:
streamlit run app.py
```

Then open your browser at **http://localhost:8501**

---

## Running the CLI

The original command-line interface is still fully functional:

```bash
# Single stock
python main.py RELIANCE --days 180

# Portfolio
python main.py RELIANCE TCS INFY HDFCBANK --days 365
```

---

## Dashboard Pages

The sidebar is split into two groups:

### QAMO — Live / Research  *(no portfolio run required)*

These pages work immediately without entering symbols or clicking Run Analysis.
Each page is self-contained and fetches its own data on demand.

---

#### 📡 Live Monitor

**What it shows:**
Real-time intraday feed for a single NSE stock.

| Section | Description |
|---------|-------------|
| Price banner | Latest Close / Open / High / Low / Volume — with ± delta vs previous bar |
| Market status | 🟢 Open / 🔴 Closed indicator |
| Feature Vector(t) | 15 computed features: Return %, Volatility, VWAP Dev, RSI(14), EMA Fast/Slow, MACD, ATR, Momentum, Volume Spike, Spread, Order Imbalance |
| Price chart | Close price line chart over selected bars |
| Volume chart | Volume bar chart |
| Feature history | Last 30 bars: price, return_pct, volatility, RSI, MACD, volume_spike, VWAP dev |
| Raw OHLCV (expandable) | Full OHLCV table for last 50 bars |

**Controls:**
- NSE Symbol — any NSE ticker without `.NS`
- Data Source — Yahoo Finance (default) · Zerodha Kite Connect · Polygon.io · Alpaca
- Interval — `1m`, `5m`, `15m`, `30m`, `1h`
- Bars — number of bars to fetch (10–500)

> Yahoo Finance works out of the box.  
> Zerodha Kite Connect, Polygon.io and Alpaca require API credentials.  
> Setup instructions are shown inline when you select those sources.

---

#### ⚛️ QAMO v2 — Adaptive Circuit

**What it shows:**
The self-evolving QAMO pipeline where the market decides the qubit count.

| Section | Description |
|---------|-------------|
| Signal banner | BUY / SELL / HOLD · P(Close>Open) · Expected return · Current qubit count n(t) |
| Confidence metrics | Confidence % · Stability % · Risk level · Complexity C(t) · n_qubits |
| Dynamic qubit allocation n(t) | Line chart of circuit size over time — flat market = 3 qubits, chaotic = up to 12 |
| Complexity C(t) | Shannon entropy + PCA rank + decorrelation score over time |
| Qubit count distribution (expandable) | Bar chart of how often each qubit count was used |
| Current state \|ψ(t)⟩ | Per-qubit table: feature label · Ry angle · P(\|1⟩) · Bloch-Z |
| Predicted next state \|ψ(t+1)⟩ | Same table for the predicted state one bar ahead |
| Quantum Trajectory | Velocity (dψ/dt) · Acceleration (d²ψ/dt²) · Curvature (d³ψ/dt³) — 3 charts |
| State Entropy H(ψ_t) | Entropy trend — low = stable, high = uncertain market |
| Circuit Adaptation | Learned Ry angle offsets per feature; adaptor update count and mean error |
| Similar Historical States | Top-10 nearest-neighbour matches by fidelity, with n_qubits and Next Δ% |
| AI Explanation | IBM watsonx / fallback explanation of the current signal |
| Strategy Performance | Total return / Sharpe / Win rate / Max drawdown |
| Multi-Window Feature Vector (expandable) | 5 time windows (w1–w5) × 6 features |
| Complexity Estimator Detail (expandable) | Raw complexity metrics breakdown |

**Controls:** NSE Symbol · Interval · Bars · 🔄 Refresh

> This is the flagship QAMO page. The A+B qubit allocator assigns a base count
> (A) from Shannon entropy and adds a correction (B) from PCA rank and
> decorrelation — so the circuit is never fixed; it evolves with the market.

---

#### ⚛️ QAMO v1 — Fixed Circuit

**What it shows:**
The original QAMO pipeline using a fixed 8-qubit quantum register.

| Section | Description |
|---------|-------------|
| Market status + price banner | Close / Open / High / Low / Volume / VWAP |
| Signal banner | BUY / SELL / HOLD · P(Close>Open) · P(Open>Close) · Expected return |
| Score metrics | Confidence % · Stability % · Risk · Qvel Δψ |
| Quantum State \|ψ(t)⟩ — 8-qubit | Per-qubit: feature · Ry angle · P(\|1⟩) · Bloch-Z for all 8 qubits |
| Fidelity & Velocity trend | Side-by-side charts: F(ψ_t, ψ_{t-1}) and 1−F over last 100 states |
| State Entropy H(ψ_t) | Entropy trend over last 80 states |
| Similar Historical States | Top-10 matches: rank · date · fidelity · green/next-green · Next Δ% |
| AI Explanation | IBM watsonx / fallback text explanation |
| Strategy Simulator | Equity curve + Total return / Sharpe / Win rate / Drawdown / Sortino |
| Multi-Window Feature Vector (expandable) | 5 windows × 7 features |
| Online Learning Stats (expandable) | Total predictions / accuracy / recent-20 accuracy |
| 📊 Nightly Eval button | Triggers self-evaluation: directional accuracy, return MAE, retrain flag, strategy summary |

**Controls:** NSE Symbol · Source · Interval · Bars · 🔄 Refresh · 📊 Nightly Eval

> Use this page to inspect the raw quantum state of a specific stock at a
> fixed circuit depth. Compare with QAMO v2 to see what dynamic qubit
> allocation changes in the signal.

---

#### 🔬 Model Comparison

**What it shows:**
A walk-forward benchmark of three models on the same intraday bar history:
- **Classical** — RSI + MACD + EMA crossover baseline
- **Quantum** — QAMO similarity search (fidelity-based)
- **Hybrid** — Quantum signal filtered by confidence ≥ 40%

| Section | Description |
|---------|-------------|
| Model Comparison table | 6 metrics side-by-side: Directional Accuracy · Sharpe · Win Rate · Total Return · Max Drawdown · Avg Latency |
| Best Model by Metric | 🏆 winner per metric with numeric value |
| Detailed Results (expandable) | Full metrics dict per model |

**Controls:** NSE Symbol · Interval · Bars · Top-k · ▶ Run Validation

> Run this page to answer: *does quantum prediction actually beat a classical
> baseline on the same data?*  
> Hybrid typically wins on risk-adjusted metrics when the market is trending.

---

#### 🧪 Trajectory Experiment

**What it shows:**
A controlled experiment comparing **Static** (morning-forecast, no updates)
vs **Adaptive** (bar-by-bar self-correction) intraday prediction.
Uses 5-min bars only. No look-ahead bias.

**Tab 1 — Single Day Experiment**

| Section | Description |
|---------|-------------|
| Benchmark Metrics table | Avg Fidelity · Dir Accuracy · MAE · RMSE · Avg Confidence · Entropy Accuracy · Sharpe — Static vs Adaptive vs Δ with winner flag |
| Chart 1 — Price Trajectory | Actual close · Static predicted · Adaptive predicted over the prediction day |
| Chart 2 — Fidelity F(ψ̂, ψ) | Static vs Adaptive fidelity per bar — higher adaptive = self-correction is working |
| Chart 3 — Model Confidence | Static vs Adaptive confidence per bar |
| Chart 4 — State Entropy | Predicted vs Actual entropy — tests if model tracks Stable→Volatile→Chaotic transitions |
| Per-Bar Comparison (expandable) | Full bar-by-bar table for adaptive mode |

Controls: NSE Symbol · Prediction Date · Training Days · Top-k · ▶ Run Experiment

**Tab 2 — Walk-Forward Validation**

| Section | Description |
|---------|-------------|
| Aggregate Summary | Mean ± std across all days for: Avg Fidelity · Dir Accuracy · MAE · RMSE · Sharpe |
| Per-Day Results table | All evaluated dates with static/adaptive metrics per day |
| Δ Fidelity bar chart | (Adaptive − Static) fidelity per day — positive = adaptive wins that day |

Controls: NSE Symbol · Start Date · End Date · Training Days · ▶ Run Walk-Forward

> Yahoo Finance 5-min data supports ~60 calendar days lookback.
> Use ≤ 30 training days to stay within the available window.

---

### Portfolio Analysis  *(requires symbols + Run Analysis)*

Enter at least 2 NSE symbols in the sidebar, choose historical days, and click
**Run Analysis**. The full pipeline runs once and all portfolio pages are
available until the page is refreshed.

---

#### Portfolio Overview

Top metric cards (best probability, lowest risk, highest gain, highest
correlation pair), full comparison table, probability and volatility bar charts,
classical correlation heatmap.

---

#### Classical Analysis

Per-stock selector. Shows: price + 20/50/100-day MA chart, daily returns
histogram, volume chart, full statistics table, BUY / HOLD natural language
insight.

---

#### Quantum Encoding & Fidelity

5-qubit product state per stock.  
Qubit angle table, P(|1⟩) grouped bar chart per stock, quantum fidelity
heatmap, pairwise fidelity rankings (most/least similar pairs).

---

#### Entanglement

CNOT-entangled pair analysis.  
Pairs table (entropy, concurrence, Bell state), quantum vs classical scatter
plot, entropy heatmap, highest/lowest entanglement pair metrics.

---

#### QFT Periodicity

Dominant trading cycle detection via Quantum Fourier Transform on return series.  
Dominant cycle summary, full frequency spectrum chart per stock, top-5 peaks
table with period in days.

---

#### Phase Estimation (QPE)

Quantum Phase Estimation cross-check of P(up).  
Classical vs QPE P(up) comparison table, confidence bars per stock, phase bin
distribution chart.

---

#### Portfolio Optimizer (VQC)

Variational Quantum Circuit portfolio allocation.  
Allocation table (weight, weight%, recommendation), pie chart, VQC vs
equal-weight bar chart, Sharpe ratio comparison.

> Recommendation labels: **STRONG BUY** ≥ 25% · **BUY** 15–25% · **HOLD** 8–15% · **AVOID** < 8%

---

#### Export Report

One-click generate and download `Portfolio_Report.md` and
`portfolio_optimizer.json`.

---

## Running the Code

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `symbols` | Yes | — | One or more NSE ticker symbols (space-separated) |
| `--days` / `-d` | No | 365 | Number of historical calendar days to analyse (1–730) |

---

### Mode 1 — Single Stock

Runs the classical pipeline only (no portfolio / quantum sections).

```bash
python main.py RELIANCE --days 180
```

**What runs:**
- Data download / cache load
- Statistical analysis (returns, probabilities, streaks, trend, volume)
- Natural language insights
- CSV + JSON report export
- Price, returns and volume charts

**Sample output:**

```
========================================================================
      QAMO — Quantum Adaptive Market Observer v5.3.0
========================================================================

Analyzing RELIANCE

Trading Days          : 180
Green Days            : 87
Red Days              : 93
Probability Up        : 48.33%   (P(Close > Open))
Probability Down      : 51.67%   (P(Open > Close))
Average Gain          : 0.87%
Average Loss          : -0.80%
Volatility            : 1.31
Longest Green Streak  : 7 days
Longest Red Streak    : 9 days

Overall Recommendation : BUY.
```

---

### Mode 2 — Portfolio (2 or more stocks)

Full pipeline — classical analysis + all quantum modules + VQC optimiser.

```bash
python main.py RELIANCE TCS INFY HDFCBANK --days 365
```

**What runs (in order):**

```
 1. Data loading           → downloads or reads from cache
 2. Classical analysis     → returns, probabilities, volatility per stock
 3. Portfolio comparison   → side-by-side table
 4. Correlation matrix     → Pearson + heatmap PNG
 5. Executive summary      → best stock by each metric
 6. Stock insights         → BUY / HOLD recommendation per stock
 7. JSON + Markdown report → portfolio_complete.json, Portfolio_Report.md
 8. Quantum encoding       → 5-qubit state per stock (Ry gates)
 9. Fidelity matrix        → |<ψi|ψj>|² + heatmap PNG
10. Entanglement analysis  → CNOT entropy, concurrence, Bell states
11. QFT periodicity        → dominant trading cycles per stock
12. Phase estimation (QPE) → quantum cross-check of P(up) per stock
13. VQC portfolio optimiser→ optimal weights + Sharpe ratio
14. watsonx AI report      → skipped if credentials not set
```

**Sample portfolio output (quantum section):**

```
========================================================================
Quantum Portfolio  (Multi-Qubit v3.0  —  5 qubits per stock)
========================================================================

HDFCBANK
--------
  q0 Probability  Ry=+1.6064 rad  P(|1>)=0.5178
  q1 Volatility   Ry=+0.7794 rad  P(|1>)=0.1443
  q2 Momentum     Ry=+2.2777 rad  P(|1>)=0.8247
  q3 Trend        Ry=+1.4376 rad  P(|1>)=0.4336
  q4 Volume       Ry=+1.6687 rad  P(|1>)=0.5489

========================================================================
Quantum Portfolio Optimizer  (VQC v3.0)
========================================================================
  Ansatz  : Ry(encode) → CNOT ring → Ry(variational)
  Stocks  : 4   Optimizer : COBYLA
  Iterations : 134   Converged : Yes

  Symbol       Weight   Weight%   Rec
  HDFCBANK     0.3790   37.90%    STRONG BUY  ███████████████
  RELIANCE     0.2510   25.10%    STRONG BUY  ██████████
  INFY         0.2278   22.78%    BUY         █████████
  TCS          0.1422   14.22%    HOLD        █████

  Sharpe Ratio  : 1.1736
  vs Equal-Weight : ↑ 3.7%
========================================================================
```

---

### More examples

```bash
# Nifty IT basket — 1 year
python main.py TCS INFY WIPRO HCLTECH LTIM --days 365

# Nifty Bank basket — 6 months
python main.py HDFCBANK ICICIBANK KOTAKBANK AXISBANK --days 180

# Single stock — 90 days
python main.py RELIANCE --days 90

# Large portfolio — 8 stocks
python main.py RELIANCE TCS INFY HDFCBANK WIPRO LTIM BAJFINANCE TITAN --days 365
```

---

### Cache behaviour

Downloaded data is saved to `data/<SYMBOL>_<DAYS>.csv` and reused on
subsequent runs. To force a fresh download, delete the relevant CSV file:

```bash
# Force fresh download for RELIANCE 365 days
rm data/RELIANCE_365.csv
```

5-min intraday data is cached separately under `data/hist_cache/`.

---

## Project Structure

```
stock-analysis/
│
├── main.py                  Entry point — argument parsing and pipeline orchestration
├── config.py                Central configuration (paths, constants, watsonx credentials)
├── analyzer.py              Statistical analysis (returns, probabilities, streaks, trend, volume)
├── data_loader.py           Yahoo Finance download + local CSV cache
├── portfolio.py             Multi-stock portfolio manager
├── comparison.py            Side-by-side portfolio comparison table
├── correlation.py           Pearson correlation matrix + heatmap
├── insights.py              Natural language insight generator per stock
├── portfolio_summary.py     Executive portfolio summary printer
├── portfolio_export.py      Full portfolio JSON export
├── markdown_report.py       Portfolio markdown report export
├── report.py                Single-stock CSV + JSON report
├── visualization.py         Price, return and volume charts
├── prompt_builder.py        Builds watsonx AI prompt from portfolio data
├── ai_report.py             IBM watsonx Granite AI integration
├── watsonx_client.py        watsonx API client
├── cache.py                 Cache utility helpers
├── logger.py                Rotating file + console logger
├── models.py                Shared data models
│
├── quantum/                 Portfolio-level quantum modules (v2.6 – v3.0)
│   ├── quantum_state.py         MultiQubitState — 5-qubit product state per stock
│   ├── quantum_encoder.py       Encodes 5 market features → 5 Ry rotation angles
│   ├── quantum_circuit.py       Builds and simulates 5-qubit Qiskit circuit
│   ├── portfolio_quantum.py     Runs quantum encoding for entire portfolio
│   ├── fidelity.py              Fidelity calculator — |<ψ1|ψ2>|²
│   ├── fidelity_matrix.py       Pairwise fidelity matrix for portfolio
│   ├── fidelity_heatmap.py      Fidelity heatmap PNG export
│   ├── entanglement_pair.py     CNOT entanglement — entropy, concurrence, Bell state
│   ├── entanglement_matrix.py   Pairwise entanglement for all portfolio pairs
│   ├── entanglement_report.py   Prints and exports entanglement results
│   ├── qft_analyzer.py          QFT periodicity detection on return series
│   ├── qft_portfolio.py         Runs QFT for every stock in portfolio
│   ├── qft_report.py            Prints dominant cycles + exports CSV/JSON
│   ├── qpe_analyzer.py          Quantum Phase Estimation — estimates P(up) via phase kickback
│   ├── qpe_portfolio.py         Runs QPE for every stock in portfolio
│   ├── qpe_report.py            Prints phase estimates + exports CSV/JSON
│   ├── vqc_optimizer.py         VQC — Ry encode + CNOT ring + Ry variational + COBYLA
│   ├── portfolio_optimizer.py   Runs VQC optimisation for full portfolio
│   ├── optimizer_report.py      Prints allocation + Sharpe + exports CSV/JSON
│   └── bloch_visualizer.py      Bloch sphere visualisation utility
│
├── live/                    QAMO intraday engine (v5.1 – v5.3)
│   ├── feed_base.py             Abstract LiveFeed + Bar dataclass
│   ├── yahoo_feed.py            Yahoo Finance adapter
│   ├── zerodha_feed.py          Zerodha Kite Connect adapter
│   ├── polygon_feed.py          Polygon.io stub
│   ├── alpaca_feed.py           Alpaca stub
│   ├── tick_buffer.py           FIFO ring buffer
│   ├── feature_generator.py     Single-window feature vector (15 features)
│   ├── multi_window_features.py 5-window feature matrix (w1–w5)
│   ├── intraday_encoder.py      Fixed 8-qubit encoder (QAMO v1)
│   ├── quantum_memory.py        10k-state ring buffer
│   ├── state_database.py        Parquet persistence (pyarrow)
│   ├── quantum_similarity.py    Fidelity-based similarity search
│   ├── prediction_engine.py     BUY / SELL / HOLD signal generator
│   ├── online_engine.py         Walk-forward online learning
│   ├── confidence_score.py      Direction + confidence + stability + risk
│   ├── hybrid_ai.py             IBM watsonx explanation
│   ├── strategy_simulator.py    Sharpe / Sortino / drawdown simulator
│   ├── self_evaluation.py       Nightly error analysis and retrain flag
│   ├── validation_engine.py     Classical vs Quantum vs Hybrid benchmark
│   ├── qamo_engine.py           QAMO v1 orchestrator (fixed 8-qubit)
│   ├── complexity_estimator.py  Shannon entropy + PCA rank → C(t)
│   ├── qubit_allocator.py       A+B dynamic qubit allocator
│   ├── adaptive_encoder_v2.py   n-qubit learnable encoder
│   ├── adaptive_memory.py       Variable-dimension state buffer
│   ├── trajectory_engine.py     Velocity / acceleration / curvature
│   ├── circuit_adaptor.py       Real-time Ry angle correction
│   ├── next_state_predictor_v2.py  Predict |ψ(t+1)⟩
│   ├── qamo_engine_v2.py        QAMO v2 orchestrator (adaptive circuit)
│   ├── trading_calendar.py      NSE trading calendar + holiday list
│   ├── historical_loader.py     N trading-day 5-min bars + file cache
│   ├── experiment_metrics.py    Fidelity / MAE / RMSE / Sharpe / dir_acc
│   ├── state_comparator.py      Per-bar ψ̂ vs ψ comparison table
│   ├── experiment_runner.py     Static + Adaptive experiment runner
│   └── walk_forward.py          Date-range walk-forward validator
│
├── dashboard/               Streamlit page modules
│   ├── runner.py                Portfolio pipeline orchestrator
│   ├── page_live_monitor.py     📡 Live Monitor
│   ├── page_qamo_v2.py          ⚛️ QAMO v2 — Adaptive Circuit
│   ├── page_qamo.py             ⚛️ QAMO v1 — Fixed Circuit
│   ├── page_validation.py       🔬 Model Comparison
│   ├── page_experiment.py       🧪 Trajectory Experiment
│   ├── page_overview.py         Portfolio Overview
│   ├── page_classical.py        Classical Analysis
│   ├── page_quantum.py          Quantum Encoding & Fidelity
│   ├── page_entanglement.py     Entanglement
│   ├── page_qft.py              QFT Periodicity
│   ├── page_qpe.py              Phase Estimation (QPE)
│   ├── page_optimizer.py        Portfolio Optimizer (VQC)
│   └── page_report.py           Export Report
│
├── data/                    Cached CSV files (auto-created)
│   └── hist_cache/          5-min bar Parquet cache
├── output/
│   ├── charts/              PNG charts (price, returns, volume, heatmaps)
│   └── reports/             CSV and JSON reports
├── logs/                    Rotating log file
│
├── requirements.txt
└── README.md
```

---

## Pipeline — Step by Step

When you run `python main.py RELIANCE TCS INFY HDFCBANK --days 365`,
the following pipeline executes in order:

```
1.  Data Loading
    └── Downloads or loads cached OHLCV data for each symbol

2.  Classical Analysis  (analyzer.py)
    ├── Daily returns and % change
    ├── Green / Red day probabilities
    │     P(Up)   = P(Close > Open)
    │     P(Down) = P(Open > Close)
    ├── Average gain / average loss
    ├── Volatility (std dev of daily returns)
    ├── Longest green and red streaks
    ├── Moving averages (20, 50, 100 day)
    ├── Trend slope (linear regression of close prices)
    └── Average volume (millions)

3.  Portfolio Comparison  (comparison.py)
    └── Side-by-side table of all stocks

4.  Classical Correlation  (correlation.py)
    ├── Pearson correlation matrix
    ├── Correlation CSV export
    └── Correlation heatmap PNG

5.  Portfolio Executive Summary  (portfolio_summary.py)
    └── Best stock by each metric

6.  Individual Stock Insights  (insights.py)
    └── Natural language recommendation per stock

7.  Portfolio JSON + Markdown Report
    ├── portfolio_complete.json
    └── Portfolio_Report.md

8.  Quantum Portfolio  (quantum_state.py + quantum_encoder.py)
    └── 5-qubit state per stock:
        q0 = Probability   Ry(2·arcsin(√P_up))
        q1 = Volatility    Ry(π · vol/MAX_VOL)
        q2 = Momentum      Ry(π/2 · (1 + momentum))
        q3 = Trend         Ry(π/2 · (1 + trend))
        q4 = Volume        Ry(π · vol/MAX_VOLUME)

9.  Quantum Fidelity Matrix  (fidelity_matrix.py)
    ├── |<ψi|ψj>|² for all stock pairs (32-dim space)
    ├── Fidelity CSV export
    └── Fidelity heatmap PNG

10. Portfolio Entanglement  (entanglement_pair.py)
    ├── CNOT-entangle q0 of each stock pair
    ├── von Neumann entropy (0=separable, 1=max entangled)
    ├── Concurrence
    ├── Bell state classification (Φ+, Φ−, Ψ+, Ψ−)
    ├── Quantum vs Classical correlation comparison
    ├── Entropy + Concurrence matrices
    └── CSV + JSON export

11. QFT Periodicity  (qft_analyzer.py)
    ├── Amplitude-encode returns → QFT (8 qubits, 256 points)
    ├── Extract top-5 dominant frequency peaks
    ├── Translate bins → trading-day periods
    └── CSV + JSON export

12. Quantum Phase Estimation  (qpe_analyzer.py)
    ├── Unitary U = Ry(θ_q0) for each stock
    ├── 6 counting qubits → 64 phase bins (resolution ≈ 1.56%)
    ├── Phase kickback + IQFT → φ_est → P(up) estimate
    ├── Cross-check vs classical P(up)
    └── CSV + JSON export

13. VQC Portfolio Optimizer  (vqc_optimizer.py)
    ├── Ansatz: Ry(encode) → CNOT ring → Ry(variational)
    ├── Cost: −Sharpe = −(Σ wᵢμᵢ) / √(wᵀ Σ w)
    ├── Optimizer: COBYLA (derivative-free, ~100-200 iterations)
    ├── Output: optimal weights, Sharpe, expected return, risk
    ├── Recommendation per stock (STRONG BUY / BUY / HOLD / AVOID)
    └── CSV + JSON export

14. IBM watsonx AI Report  (ai_report.py)  — optional
    └── Granite model generates natural language investment report
```

---

## Reading the Output

After each run the analyzer produces three categories of output:
a **full Markdown report**, **CSV/JSON data files**, and **PNG charts**.

---

### The Markdown Report  (`output/reports/Portfolio_Report.md`)

| Section | What to look for |
|---------|-----------------|
| **Portfolio Summary** | Quick-glance best stock by probability, gain, volatility |
| **Portfolio Comparison table** | Side-by-side of all stocks — high P(Up) + low Volatility |
| **Correlation Matrix** | Values ≈ 1 = moves together (less diversified). Values ≈ 0 or negative = good diversification |
| **Individual Stock Analysis** | Per-stock stats + charts + BUY/HOLD/SELL insight |
| **Quantum Encoding** | Ry angles and P(\|1>) per qubit — higher q0 P(\|1>) = higher probability |
| **Quantum Fidelity** | High fidelity (> 0.95) = stocks behave similarly in quantum space |
| **Entanglement** | High entropy/concurrence = strong quantum link even when classical correlation is low |
| **QFT Periodicity** | Dominant trading cycle in days — useful for timing entries/exits |
| **QPE** | Quantum cross-check of P(up) — high confidence = robust estimate |
| **VQC Optimizer** | STRONG BUY = highest quantum-optimised allocation weight |

---

### Charts  (`output/charts/`)

| File | How to read it |
|------|---------------|
| `<SYMBOL>_price.png` | Closing price with 20/50/100-day MAs. Uptrend = price above all MAs. |
| `<SYMBOL>_returns.png` | Daily return histogram. Narrow + centred = low volatility. Wide = high risk. |
| `<SYMBOL>_volume.png` | Trading volume over time. Spikes often coincide with news events. |
| `portfolio_correlation.png` | Classical correlation heatmap. Dark = highly correlated pairs. |
| `portfolio_fidelity_heatmap.png` | Quantum fidelity heatmap. Bright = quantum-similar stocks. |

---

### CSV Files  (`output/reports/`)

| File | Contents |
|------|---------|
| `<SYMBOL>_report.csv` | Full OHLCV data + daily returns, % change, green/red flag |
| `portfolio_correlation.csv` | Pearson correlation matrix (raw numbers) |
| `portfolio_fidelity.csv` | Quantum fidelity matrix |
| `portfolio_entanglement_entropy.csv` | Von Neumann entropy per stock pair |
| `portfolio_entanglement_concurrence.csv` | Concurrence per stock pair |
| `portfolio_qft_peaks.csv` | Top-5 frequency peaks per stock with period in days |
| `portfolio_qpe.csv` | QPE phase estimate, P(up) estimate, error, confidence per stock |
| `portfolio_optimizer.csv` | VQC optimal weights and recommendations |

---

### JSON Files  (`output/reports/`)

| File | Contents |
|------|---------|
| `<SYMBOL>_summary.json` | Classical analysis summary for one stock |
| `portfolio_complete.json` | Full classical portfolio data |
| `portfolio_entanglement.json` | All pair entanglement metrics |
| `portfolio_qft.json` | QFT results with top peaks per stock |
| `portfolio_qpe.json` | QPE results with phase bins per stock |
| `portfolio_optimizer.json` | VQC result with weights, Sharpe, allocation |
| `watsonx_prompt.txt` | The exact prompt sent (or ready to send) to watsonx |

---

### Understanding Recommendations

| Label | Meaning |
|-------|---------|
| **STRONG BUY** | VQC weight ≥ 25% — highest quantum-optimised allocation |
| **BUY** | VQC weight 15–25% — good allocation candidate |
| **HOLD** | VQC weight 8–15% — include but don't overweight |
| **AVOID** | VQC weight < 8% — quantum optimizer found low value here |

> These labels are derived from **historical data and quantum simulation only**.
> They are not financial advice.

---

## Quantum Modules

### Quantum Encoding (v2.6)

Each stock is represented as a **5-qubit product state** in a 2⁵ = 32-dimensional
Hilbert space. Each qubit independently encodes one market feature via a single
Ry rotation:

| Qubit | Feature | Encoding Formula |
|-------|---------|-----------------|
| q0 | Probability Up | `Ry(2·arcsin(√P_up))` |
| q1 | Volatility | `Ry(π · clamp(vol / 5.0))` |
| q2 | Momentum | `Ry(π/2 · (1 + clamp((green−red) / 20)))` |
| q3 | Trend | `Ry(π/2 · (1 + clamp(slope / 0.5)))` |
| q4 | Volume | `Ry(π · clamp(avg_vol_M / 50.0))` |

### Quantum Fidelity (v2.6)

Measures quantum state similarity between stocks:

```
F(ψ₁, ψ₂) = |⟨ψ₁|ψ₂⟩|²   ∈ [0, 1]
```

Computed over the full 32-element statevector (tensor product of 5 qubits).

### Portfolio Entanglement (v2.7)

Two stocks are quantum-entangled via a CNOT gate on their q0 qubits:

```
|ψ_A⟩ ⊗ |ψ_B⟩  →  CNOT(A→B)  →  |ψ_AB⟩
```

From the resulting 4-element statevector:
- **Entropy** = von Neumann entropy of reduced density matrix ρ_A (0=separable, 1=Bell state)
- **Concurrence** = `2|α₀₀α₁₁ − α₀₁α₁₀|` (entanglement measure)
- **Bell State** = closest Bell state (Φ+, Φ−, Ψ+, Ψ−)

### QFT Periodicity (v2.8)

Detects hidden cycles in daily return series:

```
Returns → Amplitude Encoding → QFT (n qubits) → Frequency Peaks → Periods (days)
```

- Up to 8 qubits → 256 data points
- Identifies top-5 dominant trading cycles per stock

### Quantum Phase Estimation (v2.9)

Estimates P(up) for each stock using QPE:

```
U = Ry(θ_q0)   →   eigenphase φ = θ/2
6 counting qubits → 64 bins → φ_est → θ_est → P(up)_est
```

Provides a quantum cross-check of the classical probability estimate.

### VQC Portfolio Optimizer (v3.0)

Optimises portfolio weights using a Variational Quantum Circuit:

```
Ansatz:   Ry(θ_enc) → CNOT ring → Ry(φ_var)
Weights:  wᵢ = softmax(P(|1>)ᵢ from VQC)
Cost:     −Sharpe = −(Σ wᵢμᵢ) / √(wᵀ·Cov·w + ε)
Solver:   COBYLA (scipy)
```

### QAMO Intraday Engine — Fixed Circuit (v5.1)

14-stage pipeline: Live Feed → Tick Buffer → Feature Generator →
8-qubit Encoder → Quantum Memory → Fidelity Similarity Search →
Prediction Engine → Confidence Score → AI Explanation → Strategy Simulator →
Self Evaluation → Online Learning → Validation → Research Dashboard.

- Probability labels: **P(Up) = P(Close > Open)**, **P(Down) = P(Open > Close)**

### QAMO Adaptive Engine — Dynamic Qubit Allocation (v5.2)

Extends QAMO v1 with a self-evolving circuit:

- **Complexity C(t)** = Shannon entropy (15 features) + PCA rank + decorrelation score
- **Qubit allocator**: n(t) = A + B where A = entropy-driven base, B = ±correction from PCA rank
- **Adaptive encoder**: n-qubit learnable Ry encoder; angle offsets corrected bar-by-bar
- **Trajectory engine**: velocity (dψ/dt), acceleration (d²ψ/dt²), curvature (d³ψ/dt³)
- **Next-state predictor**: predicts |ψ(t+1)⟩ from trajectory + similarity matches

### Quantum Trajectory Experiment Engine (v5.3)

Static vs Adaptive controlled experiment on 5-min bars:

- **Static mode**: encodes all training states once at market open; no intraday updates
- **Adaptive mode**: re-encodes and self-corrects every bar
- **Metrics**: Fidelity F(ψ̂, ψ), Directional Accuracy, MAE, RMSE, Avg Confidence, Entropy Accuracy, Sharpe
- **Walk-forward validator**: runs the experiment over every trading day in a date range; aggregates mean ± std per metric

---

## Output Files

After running a portfolio analysis, the following files are created:

```
output/
├── charts/
│   ├── <SYMBOL>_price.png              Price + moving averages
│   ├── <SYMBOL>_returns.png            Daily return distribution
│   ├── <SYMBOL>_volume.png             Trading volume
│   ├── portfolio_correlation.png       Classical correlation heatmap
│   └── portfolio_fidelity_heatmap.png  Quantum fidelity heatmap
│
└── reports/
    ├── <SYMBOL>_report.csv             Single-stock statistics
    ├── <SYMBOL>_summary.json           Single-stock JSON summary
    ├── portfolio_correlation.csv       Pearson correlation matrix
    ├── portfolio_complete.json         Full portfolio JSON
    ├── Portfolio_Report.md             Markdown portfolio report
    ├── portfolio_fidelity.csv          Quantum fidelity matrix
    ├── portfolio_entanglement_entropy.csv
    ├── portfolio_entanglement_concurrence.csv
    ├── portfolio_entanglement.json
    ├── portfolio_qft_peaks.csv         QFT frequency peaks
    ├── portfolio_qft.json
    ├── portfolio_qpe.csv               QPE phase estimates
    ├── portfolio_qpe.json
    ├── portfolio_optimizer.csv         VQC optimal weights
    ├── portfolio_optimizer.json
    └── watsonx_prompt.txt              AI prompt (always saved)
```

QAMO intraday data is cached under `data/hist_cache/` as Parquet files
(requires `pyarrow`). Quantum states are persisted under `data/qamo_states/`.

---

## IBM watsonx AI (Optional)

The AI report is skipped gracefully if credentials are not configured.
To enable it, set the following environment variables before running:

```bash
export WATSONX_API_KEY="your-api-key"
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
export WATSONX_PROJECT_ID="your-project-id"
```

Or edit `config.py` directly:

```python
WATSONX_API_KEY        = "your-api-key"
WATSONX_URL            = "https://us-south.ml.cloud.ibm.com"
WATSONX_PROJECT_ID     = "your-project-id"
WATSONX_MODEL          = "ibm/granite-3-8b-instruct"
```

The AI prompt is always saved to `output/reports/watsonx_prompt.txt`
regardless of whether credentials are configured.

---

## Version History

| Version | Feature |
|---------|---------|
| 2.4.0 | Classical probability analyzer — P(Up)/P(Down), streaks, returns |
| 2.5.0 | Rich Encoding — 4-gate single-qubit state (Ry, Rz, Rx, Phase) |
| 2.6.0 | Multi-Qubit Encoding — 5-qubit product state per stock |
| 2.7.0 | Portfolio Entanglement — CNOT, entropy, concurrence, Bell states |
| 2.8.0 | QFT Periodicity — dominant trading cycles from return series |
| 2.9.0 | Quantum Phase Estimation — P(up) via phase kickback + IQFT |
| 3.0.0 | Quantum Portfolio Optimizer — VQC + COBYLA Sharpe maximisation |
| 3.1.0 | Interactive Streamlit Dashboard — 8 portfolio pages |
| 4.1.0 | Quantum State Trajectory Engine — state evolution, velocity, acceleration, regime detection, next-state prediction, walk-forward learning |
| 5.1.0 | QAMO — full 14-stage intraday quantum pipeline (Live Feed → Prediction → Strategy) |
| 5.2.0 | QAMO v2 — self-evolving adaptive quantum encoder, A+B dynamic qubit allocator, trajectory curvature, predicted \|ψ(t+1)⟩ |
| **5.3.0** | **Quantum Trajectory Experiment Engine — static vs adaptive controlled experiment, 5-min bar prediction, walk-forward validation across date ranges, NSE trading calendar** |

---

## Disclaimer

This project is for **educational and research purposes only**.
It does not provide financial advice or guarantee future stock performance.
All analysis is based on historical data and quantum simulation.

---

## Author

**Alok Kataria**

Interest areas: Cloud Engineering · Quantum Computing · AI + Quantum Applications

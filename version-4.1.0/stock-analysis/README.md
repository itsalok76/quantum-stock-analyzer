# Quantum Stock Probability Analyzer

**Version 4.1.0** — Quantum State Trajectory Engine

A Python + Qiskit + Streamlit framework that combines classical financial
analytics with quantum computing to analyse NSE stocks, encode market features
into quantum states, optimise portfolio allocation using a Variational Quantum
Circuit, and now track, predict and continuously learn from the **evolution of
quantum states over time** — presented in an interactive web dashboard.

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
| yfinance | 0.2.65 | NSE historical data download |
| pandas | 2.2.2 | DataFrames and time series |
| numpy | 2.0.0 | Numerical computation |
| matplotlib | 3.9.0 | Price, return and volume charts |
| scipy | 1.14.0 | VQC optimiser (COBYLA) |
| plotly | 6.0.0 | Interactive correlation heatmaps |
| tabulate | 0.9.0 | Console table formatting |
| colorama | 0.4.6 | Coloured terminal output |
| ibm-watsonx-ai | 1.1.20 | IBM Granite AI report (optional) |
| qiskit | 1.0.0 | Quantum circuit construction |
| qiskit-aer | 0.14.0 | Quantum circuit simulation |

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

The dashboard is the primary interface for v4.1. It runs the full pipeline
interactively — no command line arguments needed.

```bash
# With the virtual environment active:
streamlit run app.py
```

Then open your browser at **http://localhost:8501**

**How to use:**
1. Enter NSE symbols in the sidebar (e.g. `RELIANCE TCS INFY HDFCBANK`)
2. Choose number of historical days (1–730)
3. Click **Run Analysis** — the full pipeline runs with progress spinners
4. Navigate between pages using the sidebar radio buttons
5. Click **Export Report** to download `Portfolio_Report.md` and JSON files

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

| Page | What it shows |
|------|--------------|
| **Portfolio Overview** | Top metric cards, comparison table, probability/volatility bar charts, correlation heatmap |
| **Classical Analysis** | Per-stock selector — price+MA chart, returns histogram, volume chart, full stats table, BUY/HOLD insight |
| **Quantum Encoding & Fidelity** | Qubit angle table, P(\|1>) grouped bar chart, fidelity heatmap, pairwise fidelity rankings |
| **Entanglement** | Pairs table, quantum vs classical scatter plot, entropy heatmap, highest/lowest entanglement metrics |
| **QFT Periodicity** | Dominant cycle summary, full frequency spectrum chart per stock, top-5 peaks table |
| **Phase Estimation (QPE)** | Classical vs QPE P(up) comparison, confidence bars, phase bin distribution chart |
| **Portfolio Optimizer (VQC)** | Allocation table, pie chart, VQC vs equal-weight bar chart, Sharpe comparison |
| **Quantum Trajectory** ⭐ NEW | State evolution fidelity chart, velocity & acceleration, regime timeline (Stable/Reversal/Breakout/Shock), top-k nearest-neighbour matches, next-day forecast P(up)/P(down)/confidence, walk-forward accuracy |
| **Export Report** | One-click generate + download `Portfolio_Report.md` and `portfolio_optimizer.json` |

---

## Running the Code

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `symbols` | Yes | — | One or more NSE ticker symbols (space-separated) |
| `--days` / `-d` | No | 365 | Number of historical calendar days to analyse (1–730) |

---

### Mode 1 — Single Stock

Analyse one stock. Runs the classical pipeline only (no portfolio/quantum sections).

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
      Quantum Stock Probability Analyzer v3.0.0
========================================================================

Analyzing RELIANCE

Trading Days          : 180
Green Days            : 87
Red Days              : 93
Probability Up        : 48.33%
Probability Down      : 51.67%
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
├── quantum/
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
├── data/                    Cached CSV files (auto-created)
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
Here is how to interpret each section.

---

### The Markdown Report  (`output/reports/Portfolio_Report.md`)

This is the single most readable summary — open it in any Markdown viewer
(VS Code, GitHub, Obsidian, Typora). It contains every section in order:

| Section | What to look for |
|---------|-----------------|
| **Portfolio Summary** | Quick-glance best stock by probability, gain, volatility |
| **Portfolio Comparison table** | Side-by-side of all stocks — look for high P(Up) + low Volatility |
| **Correlation Matrix** | Values close to 1 = stocks move together (less diversified). Values close to 0 or negative = good diversification |
| **Individual Stock Analysis** | Per-stock stats + embedded price/returns/volume charts + BUY/HOLD/SELL insight |
| **Quantum Encoding** | Ry angles and P(\|1>) per qubit — higher q0 P(\|1>) = higher probability stock |
| **Quantum Fidelity** | High fidelity (> 0.95) = stocks behave similarly in quantum space |
| **Entanglement** | High entropy/concurrence = strong quantum link between stocks even when classical correlation is low |
| **QFT Periodicity** | Dominant trading cycle in days — useful for timing entries/exits |
| **QPE** | Quantum cross-check of P(up) — high confidence = robust estimate |
| **VQC Optimizer** | STRONG BUY = highest quantum-optimised allocation weight |

---

### Charts  (`output/charts/`)

| File | How to read it |
|------|---------------|
| `<SYMBOL>_price.png` | Closing price with 20/50/100-day moving averages. Uptrend = price above all MAs. |
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

Answers:
- Which stocks should I buy?
- What allocation maximises risk-adjusted return?
- How much better is quantum allocation vs equal-weight?

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
| 2.5.0 | Rich Encoding — 4-gate single-qubit state (Ry, Rz, Rx, Phase) |
| 2.6.0 | Multi-Qubit Encoding — 5-qubit product state per stock |
| 2.7.0 | Portfolio Entanglement — CNOT, entropy, concurrence, Bell states |
| 2.8.0 | QFT Periodicity — dominant trading cycles from return series |
| 2.9.0 | Quantum Phase Estimation — P(up) via phase kickback + IQFT |
| 3.0.0 | Quantum Portfolio Optimizer — VQC + COBYLA Sharpe maximisation |
| 3.1.0 | Interactive Streamlit Dashboard — 8 pages, full pipeline UI, 1–730 day slider |
| **4.1.0** | **Quantum State Trajectory Engine — state evolution, velocity, acceleration, regime detection (Stable/Reversal/Breakout/Shock), fidelity-based similarity search, next-state prediction, walk-forward online learning, adaptive encoder** |

---

## Disclaimer

This project is for **educational and research purposes only**.
It does not provide financial advice or guarantee future stock performance.
All analysis is based on historical data and quantum simulation.

---

## Author

**Alok Kataria**

Interest areas: Cloud Engineering · Quantum Computing · AI + Quantum Applications

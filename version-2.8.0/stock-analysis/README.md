# Quantum Stock Probability Analyzer

## Version 1.0 (Classical Analytics Engine)

A Python-based stock analysis framework that analyzes NSE stock price behavior using historical Open/Close data.

The project is designed as the foundation for future integration with:

- IBM watsonx AI for natural language financial insights
- Qiskit for quantum probability experiments

---

# Features

## Data Analysis

- NSE stock historical data download
- Open vs Close analysis
- Daily return calculation
- Gain/Loss analysis
- Volatility calculation
- Standard deviation
- Maximum gain/loss day
- Green/Red day statistics
- Winning and losing streak analysis

---

## Probability Analysis

The analyzer calculates:


P(Close > Open)

P(Open > Close)

Average gain probability

Average loss probability


Example:


Probability Close > Open : 58.20%

Probability Open > Close : 41.80%


---

## Technical Indicators

Currently supported:

- 20 day moving average
- 50 day moving average
- 100 day moving average

---

## Visualization

Generated charts:

### Price Trend

Shows:

- Closing price
- Moving averages


### Return Distribution

Shows:

- Daily return histogram


### Volume Trend

Shows:

- Trading volume movement

---

# Project Structure


stock-analysis/

│
├── main.py
├── config.py
├── data_loader.py
├── analyzer.py
├── visualization.py
├── report.py
│
├── requirements.txt
├── README.md
│
└── output/
|
├── charts/
|
└── reports/


---

# Installation

## 1. Clone repository

```bash
git clone <repository-url>

cd stock-analysis
2. Create virtual environment

Linux/macOS:

python3 -m venv venv

source venv/bin/activate

Windows:

python -m venv venv

venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
Usage
Analyze RELIANCE
python main.py RELIANCE 180

Meaning:

RELIANCE = NSE symbol

180 = last 180 calendar days
Other examples

TCS:

python main.py TCS 365

Infosys:

python main.py INFY 90

HDFC Bank:

python main.py HDFCBANK 180
Output

After execution:

output/

├── charts/

│   ├── RELIANCE_price.png

│   ├── RELIANCE_returns.png

│   └── RELIANCE_volume.png


└── reports/

    ├── RELIANCE_report.csv

    └── RELIANCE_summary.json
Example Report
================================================

RELIANCE Stock Analysis Report

================================================


Trading Days          : 180

Green Days            : 104

Red Days              : 76


Probability Close > Open

                      : 57.8%


Probability Open > Close

                      : 42.2%


Average Gain          : 1.12%

Average Loss          : -0.91%


Longest Green Streak  : 8 days

Longest Red Streak    : 5 days

================================================
Architecture
             NSE Market Data

                    |

                    v

             data_loader.py

                    |

                    v

             analyzer.py

                    |

        +-----------+-----------+

        |                       |

        v                       v


 visualization.py        report.py


        |

        v


      Charts


                    |

                    v


              JSON Output

                    |

                    v


          watsonx / Quantum Layer
Future Roadmap
Version 1.1

Code improvements:

Dataclass based models
Better logging
Unit testing
Improved error handling
Version 2.0

Advanced financial analytics:

RSI
MACD
Bollinger Bands
Sharpe ratio
Maximum drawdown
Beta analysis
Correlation analysis
Monte Carlo simulation
Version 3.0

IBM watsonx Integration:

The generated JSON report will be provided to watsonx.

Example:

Input:

{
 "probability_up":0.58,
 "average_gain":1.12,
 "volatility":1.5
}

Output:

The stock shows a moderate bullish tendency
with positive opening-to-closing movement
in 58% of observed sessions.
Version 4.0

Quantum Finance Extension:

Using Qiskit:

Classical probability:

P(up)=0.58

P(down)=0.42

Encoded as:

|ψ> = √0.58 |0> + √0.42 |1>

Experiments:

Quantum probability sampling
Multi-stock correlation
Quantum state representation
Quantum random walks
Disclaimer

This project is for educational and research purposes only.

It does not provide financial advice or guarantee future stock performance.

Author

Alok Kataria

Interest areas:

Cloud Engineering
Quantum Computing
AI + Quantum Applications

---

## Version 1.0 status now

```text
✅ Part 1  Project setup
✅ Part 2  Data loader
✅ Part 3  Analyzer
✅ Part 4  Visualization
✅ Part 5  Reports
✅ Part 6  README

Next is Part 7 — Final Integration + Testing.

In Part 7 we will:

Run the complete pipeline:

python main.py RELIANCE 180
Fix any integration issues (imports, paths, yfinance changes)
Add a sample output
Tag this as Version 1.0.0

After that, we can start Version 1.1 improvements.
"""
self_evaluation.py

Stage 12 — Self-Evaluation + Nightly Retraining.

Every evening:
    1. Compare all predictions vs actual market outcomes
    2. Compute error analysis (MAE, directional accuracy, by-regime)
    3. Identify which features drove the most errors
    4. Produce a retraining report
    5. Update encoder normalisation constants for next session

Version : 5.12.0
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

import numpy as np

from live.online_engine     import OnlineEngine
from live.strategy_simulator import StrategySimulator
from config                 import OUTPUT_REPORT_DIR


class SelfEvaluation:
    """
    Nightly self-evaluation engine.

    Reads the OnlineEngine history (all predictions + actuals for the day),
    computes a full error report, and returns retraining recommendations.

    Parameters
    ----------
    engine    : OnlineEngine
    simulator : StrategySimulator
    symbol    : str
    """

    def __init__(
        self,
        engine    : OnlineEngine,
        simulator : StrategySimulator,
        symbol    : str,
    ):
        self.engine    = engine
        self.simulator = simulator
        self.symbol    = symbol.upper()

    # ------------------------------------------------------------------

    def evaluate(self) -> dict:
        """
        Run full nightly evaluation.

        Returns a report dict with all metrics + retraining recommendations.
        """
        history = self.engine.history
        if not history:
            return {"status": "no_data", "symbol": self.symbol}

        n         = len(history)
        correct   = [h for h in history if h["correct"]]
        incorrect = [h for h in history if not h["correct"]]

        # Directional accuracy
        dir_acc = len(correct) / n if n else 0.0

        # Confidence calibration
        conf_correct   = np.mean([h["confidence"] for h in correct])   if correct   else 0.0
        conf_incorrect = np.mean([h["confidence"] for h in incorrect]) if incorrect else 0.0

        # Return prediction error
        ret_errors = [
            abs(h["exp_return"] - h["actual_return"])
            for h in history
            if "actual_return" in h
        ]
        mae = float(np.mean(ret_errors)) if ret_errors else 0.0

        # Strategy performance
        sim_results = self.simulator.results()

        # Retraining signal
        retrain_needed = (
            dir_acc < 0.52 or
            (conf_correct < conf_incorrect + 0.05) or
            sim_results.get("sharpe_ratio", 0) < 0.5
        )

        # Recommendations
        recommendations = []
        if dir_acc < 0.52:
            recommendations.append(
                "Directional accuracy below 52% — widen normalisation ranges "
                "to increase state diversity."
            )
        if conf_incorrect > conf_correct:
            recommendations.append(
                "Model is over-confident when wrong — reduce learning rate "
                "or increase top_k for more conservative aggregation."
            )
        if mae > 1.0:
            recommendations.append(
                "Return MAE > 1% — consider tighter max_ret normalisation."
            )
        if sim_results.get("max_drawdown_pct", 0) > 15:
            recommendations.append(
                "Max drawdown > 15% — add a volatility filter before entering positions."
            )
        if not recommendations:
            recommendations.append("Model performing within acceptable bounds.")

        report = {
            "symbol"              : self.symbol,
            "date"                : datetime.now().strftime("%Y-%m-%d"),
            "n_predictions"       : n,
            "directional_accuracy": round(dir_acc * 100, 2),
            "conf_when_correct"   : round(float(conf_correct),   4),
            "conf_when_wrong"     : round(float(conf_incorrect),  4),
            "return_mae"          : round(mae, 4),
            "strategy"            : sim_results,
            "retrain_needed"      : retrain_needed,
            "recommendations"     : recommendations,
            "learned_offsets"     : [round(o, 6) for o in self.engine.offsets],
            "learned_norm"        : {k: round(v, 4) for k, v in self.engine.encoder.norm.items()},
        }

        return report

    # ------------------------------------------------------------------

    def save_report(self, report: dict) -> Path:
        """Save the evaluation report as JSON."""
        fname = (
            OUTPUT_REPORT_DIR /
            f"qamo_eval_{self.symbol}_{report['date']}.json"
        )
        fname.write_text(json.dumps(report, indent=2, default=str))
        return fname

    # ------------------------------------------------------------------

    def print_report(self, report: dict):
        print()
        print("=" * 60)
        print(f"  QAMO Self-Evaluation — {report['symbol']}  {report['date']}")
        print("=" * 60)
        print(f"  Predictions today  : {report['n_predictions']}")
        print(f"  Directional accuracy: {report['directional_accuracy']}%")
        print(f"  Confidence (correct): {report['conf_when_correct']}")
        print(f"  Confidence (wrong)  : {report['conf_when_wrong']}")
        print(f"  Return MAE          : {report['return_mae']}%")
        sim = report.get("strategy", {})
        print(f"  Sharpe Ratio        : {sim.get('sharpe_ratio', '—')}")
        print(f"  Max Drawdown        : {sim.get('max_drawdown_pct', '—')}%")
        print(f"  Retrain needed      : {report['retrain_needed']}")
        print()
        print("  Recommendations:")
        for r in report["recommendations"]:
            print(f"    • {r}")
        print("=" * 60)

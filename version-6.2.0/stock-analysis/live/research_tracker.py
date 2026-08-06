"""
research_tracker.py

v6.2.0 — Actual vs Predicted Research Tracker.

Accumulates, within a single trading session, pairs of:
    (timestamp, actual_close, predicted_close, signal, exp_return, confidence)

Design rules
------------
* Prediction recorded at time T refers to the *next* bar T+1.
* Actual close for T is recorded when the bar at T arrives.
* Because we predict 30 minutes ahead we keep two queues:
    - _pending  : {bar_ts → prediction_dict}  written when prediction fires
    - records   : final resolved row when actual bar T+1 is observed

This gives the "prediction lags live data by 30 min" display the caller
wants: the prediction line is plotted 30 minutes *before* the bar it
targets, while the actual line reflects the close as it happens.

Version : 6.2.0
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResearchRecord:
    """One matched (actual, predicted) data point."""
    timestamp        : str          # bar timestamp (ISO-8601)
    actual_close     : float        # observed close for this bar
    predicted_close  : float        # predicted close that was made 30 min earlier
    signal           : str          # BUY / SELL / HOLD at prediction time
    exp_return       : float        # expected % return at prediction time
    confidence       : float        # confidence at prediction time
    p_up             : float        # P(up) at prediction time
    error_pct        : float = 0.0  # |actual - predicted| / actual × 100
    correct_dir      : bool  = False # did the signal match actual direction?

    def __post_init__(self):
        if self.actual_close and self.actual_close != 0:
            self.error_pct = abs(self.actual_close - self.predicted_close) \
                             / self.actual_close * 100
        actual_green    = self.actual_close >= 0  # compared to open, set externally
        predicted_green = self.p_up >= 0.5
        # direction correctness resolved externally (see resolve())


class ResearchTracker:
    """
    Session-scoped Actual vs Predicted tracker.

    Parameters
    ----------
    capacity   : int   max records to keep in memory  (default 390 = 1 trading day of 1-min bars)
    fwd_bars   : int   number of bars ahead the prediction targets  (default 30)
    """

    def __init__(self, capacity: int = 390, fwd_bars: int = 30):
        self.capacity  = capacity
        self.fwd_bars  = fwd_bars

        # circular buffer of resolved records
        self._records  : deque[ResearchRecord] = deque(maxlen=capacity)

        # pending predictions keyed by the *target* bar timestamp
        # (i.e. the bar fwd_bars ahead of when the prediction was made)
        self._pending  : dict[str, dict] = {}

        # raw price history for reference
        self._prices   : deque[tuple[str, float]] = deque(maxlen=capacity)

        # running accuracy
        self.n_total   : int = 0
        self.n_correct : int = 0

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def record_prediction(
        self,
        prediction_ts   : str,
        predicted_close : float,
        signal          : str,
        exp_return      : float,
        confidence      : float,
        p_up            : float,
        target_ts       : str = "",
    ):
        """
        Store a prediction made at prediction_ts.

        Parameters
        ----------
        prediction_ts   : timestamp when the prediction was made
        predicted_close : the predicted price value
        signal          : BUY / SELL / HOLD
        exp_return      : expected % change
        confidence      : model confidence [0,1]
        p_up            : P(up) [0,1]
        target_ts       : optional explicit timestamp for the target bar;
                          if blank, uses prediction_ts as key (caller resolves later)
        """
        key = target_ts or prediction_ts
        self._pending[key] = {
            "prediction_ts"   : prediction_ts,
            "predicted_close" : predicted_close,
            "signal"          : signal,
            "exp_return"      : exp_return,
            "confidence"      : confidence,
            "p_up"            : p_up,
        }

    def record_actual(
        self,
        bar_ts       : str,
        actual_close : float,
        actual_open  : float,
    ):
        """
        Record an observed bar; if there is a pending prediction for this
        timestamp, produce a resolved ResearchRecord.

        Parameters
        ----------
        bar_ts       : bar timestamp
        actual_close : observed close price
        actual_open  : observed open price (used for direction check)
        """
        self._prices.append((bar_ts, actual_close))

        if bar_ts in self._pending:
            pred = self._pending.pop(bar_ts)
            actual_green    = actual_close >= actual_open
            predicted_green = pred["p_up"] >= 0.5

            error_pct = 0.0
            if actual_close and actual_close != 0:
                error_pct = abs(actual_close - pred["predicted_close"]) \
                            / actual_close * 100

            rec = ResearchRecord(
                timestamp        = bar_ts,
                actual_close     = actual_close,
                predicted_close  = pred["predicted_close"],
                signal           = pred["signal"],
                exp_return       = pred["exp_return"],
                confidence       = pred["confidence"],
                p_up             = pred["p_up"],
                error_pct        = round(error_pct, 4),
                correct_dir      = (actual_green == predicted_green),
            )
            self._records.append(rec)
            self.n_total += 1
            if rec.correct_dir:
                self.n_correct += 1

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def records(self) -> list[ResearchRecord]:
        return list(self._records)

    def prices(self) -> list[tuple[str, float]]:
        """All recorded actual prices (timestamp, close)."""
        return list(self._prices)

    def pending_predictions(self) -> dict[str, dict]:
        """Predictions not yet matched to an actual bar."""
        return dict(self._pending)

    def accuracy(self) -> float:
        return round(self.n_correct / self.n_total, 4) if self.n_total else 0.0

    def mean_error_pct(self) -> float:
        recs = list(self._records)
        if not recs:
            return 0.0
        return round(sum(r.error_pct for r in recs) / len(recs), 4)

    def reset(self):
        """Clear all records (call at session start)."""
        self._records.clear()
        self._pending.clear()
        self._prices.clear()
        self.n_total   = 0
        self.n_correct = 0

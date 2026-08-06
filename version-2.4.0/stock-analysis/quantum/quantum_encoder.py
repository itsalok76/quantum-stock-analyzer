"""
quantum_encoder.py

Converts stock statistics into a QuantumState.

Version : 2.5.0

Version 2.5 — Rich Encoding:
    Four market features are each mapped to a rotation angle:

    Feature          Gate    Angle formula
    -------          ----    -------------
    Probability Up   Ry      2 * arcsin(sqrt(P_up))
    Volatility       Rz      pi * clamp(vol / MAX_VOL)
    Momentum         Rx      pi * clamp((green - red) / MAX_STREAK)
    Average Gain     Phase   pi * clamp(avg_gain / MAX_GAIN)
"""

from __future__ import annotations

import math

from quantum.quantum_state import QuantumState
from config import (
    QUANTUM_MAX_VOLATILITY,
    QUANTUM_MAX_AVG_GAIN,
    QUANTUM_MAX_STREAK,
)


def _clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


class QuantumEncoder:

    # ---------------------------------------------------------

    def __init__(self, summary: dict):

        self.summary = summary

    # ---------------------------------------------------------

    def encode(self) -> QuantumState:
        """
        Map four market features onto four rotation angles
        and return a QuantumState built from those angles.
        """

        # --------------------------------------------------
        # Ry — Probability Up
        #
        # theta = 2 * arcsin(sqrt(P_up))
        # This is the canonical amplitude encoding:
        #   Ry(theta)|0> = sqrt(P_down)|0> + sqrt(P_up)|1>
        # --------------------------------------------------

        p_up = _clamp(self.summary["ProbabilityUp"], 0.0, 1.0)

        theta_ry = 2.0 * math.asin(math.sqrt(p_up))

        # --------------------------------------------------
        # Rz — Volatility
        #
        # phi = pi * clamp(vol / MAX_VOL,  0, 1)
        # Low volatility → near 0; high volatility → near pi
        # --------------------------------------------------

        vol = self.summary["Volatility"]

        theta_rz = math.pi * _clamp(
            vol / QUANTUM_MAX_VOLATILITY,
            0.0,
            1.0
        )

        # --------------------------------------------------
        # Rx — Momentum
        #
        # mu = pi * clamp((green_streak - red_streak) /
        #                  MAX_STREAK,  -1, 1)
        # Positive momentum → positive angle;
        # Negative momentum → negative angle
        # --------------------------------------------------

        green = self.summary["LongestGreenStreak"]
        red   = self.summary["LongestRedStreak"]

        theta_rx = math.pi * _clamp(
            (green - red) / QUANTUM_MAX_STREAK,
            -1.0,
            1.0
        )

        # --------------------------------------------------
        # Phase — Average Gain
        #
        # lam = pi * clamp(avg_gain / MAX_GAIN,  0, 1)
        # Larger average gain → larger phase shift on |1>
        # --------------------------------------------------

        avg_gain = self.summary["AverageGain"]

        lam = math.pi * _clamp(
            avg_gain / QUANTUM_MAX_AVG_GAIN,
            0.0,
            1.0
        )

        return QuantumState(
            theta_ry=theta_ry,
            theta_rz=theta_rz,
            theta_rx=theta_rx,
            lam=lam,
        )

    # ---------------------------------------------------------

    def print(self) -> QuantumState:

        state = self.encode()

        state.print()

        return state

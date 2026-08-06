"""
quantum_state.py

Represents a single-qubit quantum state for a stock.

Version : 2.5.0

Version 2.5 — Rich Encoding:
    The state is now produced by applying four rotation gates
    in sequence to |0>:

        Rx(theta_rx) · Rz(theta_rz) · Ry(theta_ry) · Phase(lam) |0>

    Each angle encodes a distinct market feature:

        theta_ry  <-- Probability Up     (Ry gate)
        theta_rz  <-- Volatility         (Rz gate)
        theta_rx  <-- Momentum           (Rx gate)
        lam       <-- Average Gain       (Phase gate)
"""

from __future__ import annotations

import math
import cmath

import numpy as np


class QuantumState:
    """
    Represents

        |ψ> = α|0> + β|1>

    produced by composing four single-qubit rotation gates.

    Attributes
    ----------
    theta_ry : float   Ry angle  — encodes Probability Up
    theta_rz : float   Rz angle  — encodes Volatility
    theta_rx : float   Rx angle  — encodes Momentum
    lam      : float   Phase     — encodes Average Gain
    alpha    : complex amplitude of |0>
    beta     : complex amplitude of |1>
    """

    # ---------------------------------------------------------

    def __init__(
        self,
        theta_ry: float,
        theta_rz: float,
        theta_rx: float,
        lam: float,
    ):
        self.theta_ry = theta_ry
        self.theta_rz = theta_rz
        self.theta_rx = theta_rx
        self.lam = lam

        self.alpha, self.beta = self._compose()

    # ---------------------------------------------------------

    def _ry(self, theta: float) -> np.ndarray:
        """2x2 Ry rotation matrix."""
        c = math.cos(theta / 2)
        s = math.sin(theta / 2)
        return np.array([
            [ c, -s],
            [ s,  c]
        ], dtype=complex)

    # ---------------------------------------------------------

    def _rz(self, phi: float) -> np.ndarray:
        """2x2 Rz rotation matrix."""
        return np.array([
            [cmath.exp(-1j * phi / 2), 0],
            [0, cmath.exp( 1j * phi / 2)]
        ], dtype=complex)

    # ---------------------------------------------------------

    def _rx(self, theta: float) -> np.ndarray:
        """2x2 Rx rotation matrix."""
        c = math.cos(theta / 2)
        s = math.sin(theta / 2)
        return np.array([
            [      c, -1j * s],
            [-1j * s,       c]
        ], dtype=complex)

    # ---------------------------------------------------------

    def _phase(self, lam: float) -> np.ndarray:
        """Global phase gate — applies e^(i·lam) to |1>."""
        return np.array([
            [1,                    0],
            [0, cmath.exp(1j * lam)]
        ], dtype=complex)

    # ---------------------------------------------------------

    def _compose(self):
        """
        Apply gates left-to-right on |0>:

            Phase · Ry · Rz · Rx · |0>

        Returns (alpha, beta) complex amplitudes.
        """

        state = np.array([1.0 + 0j, 0.0 + 0j])

        state = self._ry(self.theta_ry) @ state
        state = self._rz(self.theta_rz) @ state
        state = self._rx(self.theta_rx) @ state
        state = self._phase(self.lam)   @ state

        return complex(state[0]), complex(state[1])

    # ---------------------------------------------------------

    def probability_zero(self) -> float:
        return abs(self.alpha) ** 2

    # ---------------------------------------------------------

    def probability_one(self) -> float:
        return abs(self.beta) ** 2

    # ---------------------------------------------------------

    def statevector(self) -> list:
        return [self.alpha, self.beta]

    # ---------------------------------------------------------

    def is_normalized(self) -> bool:
        total = self.probability_zero() + self.probability_one()
        return abs(total - 1.0) < 1e-10

    # ---------------------------------------------------------

    def amplitudes(self):
        return (self.alpha, self.beta)

    # ---------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "theta_ry": self.theta_ry,
            "theta_rz": self.theta_rz,
            "theta_rx": self.theta_rx,
            "lam":      self.lam,
            "alpha_real": self.alpha.real,
            "alpha_imag": self.alpha.imag,
            "beta_real":  self.beta.real,
            "beta_imag":  self.beta.imag,
            "probability_zero": self.probability_zero(),
            "probability_one":  self.probability_one(),
        }

    # ---------------------------------------------------------

    def __str__(self) -> str:

        alpha = abs(self.alpha)
        beta  = abs(self.beta)

        return (
            f"|ψ> = {alpha:.4f}|0> + {beta:.4f}e^(iφ)|1>  "
            f"[Ry={self.theta_ry:.3f} "
            f"Rz={self.theta_rz:.3f} "
            f"Rx={self.theta_rx:.3f} "
            f"λ={self.lam:.3f}]"
        )

    # ---------------------------------------------------------

    def print(self):

        print()
        print("=" * 60)
        print("Quantum State (Rich Encoding v2.5)")
        print("=" * 60)
        print(self)
        print()
        print(f"  Ry (Probability Up) = {self.theta_ry:.4f} rad")
        print(f"  Rz (Volatility)     = {self.theta_rz:.4f} rad")
        print(f"  Rx (Momentum)       = {self.theta_rx:.4f} rad")
        print(f"  λ  (Avg Gain)       = {self.lam:.4f} rad")
        print()
        print(f"  P(|0>) = {self.probability_zero():.4f}")
        print(f"  P(|1>) = {self.probability_one():.4f}")
        print(f"  Normalized : {self.is_normalized()}")
        print("=" * 60)

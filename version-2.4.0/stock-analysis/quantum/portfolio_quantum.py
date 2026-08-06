"""
portfolio_quantum.py

Creates quantum states for an entire stock portfolio.

Version : 2.5.0
"""

from __future__ import annotations

from quantum.quantum_encoder import QuantumEncoder


class QuantumPortfolio:

    # ---------------------------------------------------------

    def __init__(self, portfolio):

        """
        portfolio : PortfolioAnalyzer
        """

        self.portfolio = portfolio

        self.states = {}

    # ---------------------------------------------------------

    def build(self):

        self.states.clear()

        for symbol, analyzer in self.portfolio.analyzers.items():

            summary = analyzer.get_summary()

            state = QuantumEncoder(summary).encode()

            self.states[symbol] = state

        return self.states

    # ---------------------------------------------------------

    def get_state(self, symbol):

        return self.states[symbol]

    # ---------------------------------------------------------

    def symbols(self):

        return list(self.states.keys())

    # ---------------------------------------------------------

    def print(self):

        print()

        print("=" * 72)
        print("Quantum Portfolio  (Rich Encoding v2.5)")
        print("=" * 72)

        for symbol in self.symbols():

            state = self.states[symbol]

            print()
            print(symbol)
            print("-" * len(symbol))
            print(state)
            print()
            print(f"  Ry (Prob Up)   = {state.theta_ry:.4f} rad")
            print(f"  Rz (Volatility)= {state.theta_rz:.4f} rad")
            print(f"  Rx (Momentum)  = {state.theta_rx:.4f} rad")
            print(f"  λ  (Avg Gain)  = {state.lam:.4f} rad")
            print()
            print(f"  P(|0>) = {state.probability_zero():.4f}")
            print(f"  P(|1>) = {state.probability_one():.4f}")

        print()
        print("=" * 72)

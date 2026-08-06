"""
fidelity.py

Computes quantum fidelity between stocks.

Version : 2.5.0
"""

from __future__ import annotations

import numpy as np

from quantum.quantum_state import QuantumState


class FidelityCalculator:

    # ---------------------------------------------------------

    @staticmethod
    def fidelity(
        state1: QuantumState,
        state2: QuantumState
    ):

        psi1 = np.array(

            state1.statevector(),

            dtype=complex

        )

        psi2 = np.array(

            state2.statevector(),

            dtype=complex

        )

        overlap = np.vdot(

            psi1,

            psi2

        )

        return abs(overlap) ** 2

    # ---------------------------------------------------------

    @staticmethod
    def print(
        name1,
        state1,
        name2,
        state2
    ):

        value = FidelityCalculator.fidelity(

            state1,

            state2

        )

        print()

        print("=" * 60)

        print("Quantum Fidelity")

        print("=" * 60)

        print(

            f"{name1} ↔ {name2}"

        )

        print()

        print(

            f"Fidelity = {value:.6f}"

        )

        if value > 0.99:

            print("Interpretation : Nearly identical")

        elif value > 0.95:

            print("Interpretation : Very similar")

        elif value > 0.80:

            print("Interpretation : Moderately similar")

        else:

            print("Interpretation : Different")

        print("=" * 60)

        return value

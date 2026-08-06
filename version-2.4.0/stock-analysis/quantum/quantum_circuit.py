"""
quantum_circuit.py

Creates a Qiskit circuit from a QuantumState.

Version : 2.5.0

Version 2.5 — Rich Encoding:
    The circuit now applies four gates in sequence:

        Ry(theta_ry) → Rz(theta_rz) → Rx(theta_rx) → Phase(lam)

    Each gate encodes a distinct market feature.
"""

from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from quantum.quantum_state import QuantumState


class QuantumCircuitBuilder:

    # ---------------------------------------------------------

    def __init__(self, state: QuantumState):

        self.state = state

    # ---------------------------------------------------------

    def build(self) -> QuantumCircuit:
        """
        Prepare the rich encoded state on 1 qubit:

            Ry(theta_ry) → Rz(theta_rz) → Rx(theta_rx) → Phase(lam)

        Feature mapping:
            Ry  — Probability Up
            Rz  — Volatility
            Rx  — Momentum
            P1  — Average Gain (global phase on |1>)
        """

        qc = QuantumCircuit(1, 1)

        qc.ry(self.state.theta_ry, 0)

        qc.rz(self.state.theta_rz, 0)

        qc.rx(self.state.theta_rx, 0)

        if abs(self.state.lam) > 1e-12:
            qc.p(self.state.lam, 0)

        qc.measure(0, 0)

        return qc

    # ---------------------------------------------------------

    def simulate(self, shots: int = 4096) -> dict:

        simulator = AerSimulator()

        circuit = self.build()

        job = simulator.run(circuit, shots=shots)

        result = job.result()

        counts = result.get_counts()

        return counts

    # ---------------------------------------------------------

    def print(self, shots: int = 4096):

        print()
        print("=" * 60)
        print("Quantum Circuit (Rich Encoding v2.5)")
        print("=" * 60)

        circuit = self.build()

        print(circuit)

        counts = self.simulate(shots)

        p0 = counts.get("0", 0) / shots
        p1 = counts.get("1", 0) / shots

        print()
        print("Measurement Counts :", counts)
        print()
        print(f"P(|0>) = {p0:.4f}  (expected {self.state.probability_zero():.4f})")
        print(f"P(|1>) = {p1:.4f}  (expected {self.state.probability_one():.4f})")
        print("=" * 60)

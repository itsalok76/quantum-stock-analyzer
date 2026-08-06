"""
adaptive_memory.py

Stage 5 — Adaptive Quantum Memory.

Ring buffer that stores variable-dimension AdaptiveState objects.
Because n_qubits changes over time, states have different Hilbert
space dimensions. Cross-dimensional fidelity is computed by padding
both states to the larger dimension before taking the inner product.

Version : 5.2.0
"""

from __future__ import annotations

from collections import deque
import numpy as np

from live.adaptive_encoder_v2 import AdaptiveState


def _fidelity(s1: AdaptiveState, s2: AdaptiveState) -> float:
    """
    Fidelity between two AdaptiveStates, possibly of different dimension.
    Pads the smaller to the larger dimension before computing |⟨ψ1|ψ2⟩|².
    """
    d1 = len(s1.vector)
    d2 = len(s2.vector)
    if d1 == d2:
        v1, v2 = s1.vector, s2.vector
    elif d1 < d2:
        v1 = s1.padded_vector(d2)
        v2 = s2.vector
    else:
        v1 = s1.vector
        v2 = s2.padded_vector(d1)
    return float(abs(v1.conj() @ v2) ** 2)


class AdaptiveMemory:
    """
    Fixed-capacity ring buffer of AdaptiveState records.

    Each record:
        state       AdaptiveState
        n_qubits    int
        fv          dict   feature vector
        timestamp   str
        price       float
        green       bool
        complexity  float

    Parameters
    ----------
    capacity : int   (default 10_000)
    """

    def __init__(self, capacity: int = 10_000):
        self.capacity = capacity
        self._buf     : deque = deque(maxlen=capacity)

    # ------------------------------------------------------------------

    def append(
        self,
        state      : AdaptiveState,
        n_qubits   : int,
        fv         : dict,
        timestamp  : str,
        price      : float,
        green      : bool,
        complexity : float = 0.0,
    ):
        self._buf.append({
            "state"      : state,
            "n_qubits"   : n_qubits,
            "fv"         : fv,
            "timestamp"  : timestamp,
            "price"      : price,
            "green"      : green,
            "complexity" : complexity,
        })

    # ------------------------------------------------------------------

    def records(self) -> list[dict]:
        return list(self._buf)

    def latest(self) -> dict | None:
        return self._buf[-1] if self._buf else None

    def __len__(self) -> int:
        return len(self._buf)

    def is_empty(self) -> bool:
        return len(self._buf) == 0

    # ------------------------------------------------------------------

    def velocity(self) -> float:
        """Latest quantum velocity = 1 − F(ψ_t, ψ_{t-1})."""
        if len(self._buf) < 2:
            return 0.0
        buf = list(self._buf)
        f   = _fidelity(buf[-2]["state"], buf[-1]["state"])
        return round(1.0 - f, 6)

    # ------------------------------------------------------------------

    def search(self, query: AdaptiveState, top_k: int = 20) -> list[dict]:
        """
        Fidelity nearest-neighbour search across all stored states.
        Handles variable dimensions via padding.

        Returns list of dicts sorted by fidelity descending.
        """
        records = self.records()
        n       = len(records)
        if n == 0:
            return []

        scores = []
        for i, rec in enumerate(records):
            f = _fidelity(query, rec["state"])
            scores.append((f, i))

        scores.sort(key=lambda x: x[0], reverse=True)
        top = scores[:top_k]

        results = []
        for rank, (fidelity, idx) in enumerate(top, start=1):
            rec      = records[idx]
            next_rec = records[idx + 1] if idx + 1 < n else None
            pct      = None
            if next_rec and rec["price"] != 0:
                pct = (next_rec["price"] / rec["price"] - 1.0) * 100.0

            results.append({
                "rank"       : rank,
                "fidelity"   : round(fidelity, 6),
                "timestamp"  : rec["timestamp"],
                "price"      : rec["price"],
                "green"      : rec["green"],
                "n_qubits"   : rec["n_qubits"],
                "complexity" : rec["complexity"],
                "next_green" : next_rec["green"]  if next_rec else None,
                "next_price" : next_rec["price"]  if next_rec else None,
                "pct_change" : round(pct, 4)       if pct is not None else None,
            })

        return results

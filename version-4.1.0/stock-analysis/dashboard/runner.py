"""
runner.py

Runs the full analysis pipeline and caches results
in Streamlit session state.

Version : 4.1.0
"""

from __future__ import annotations

import streamlit as st

from data_loader import load_stock_data, DataLoaderError
from analyzer import StockAnalyzer
from portfolio import PortfolioAnalyzer
from comparison import ComparisonEngine
from correlation import CorrelationEngine
from insights import InsightEngine
from portfolio_summary import PortfolioSummary

from quantum.quantum_encoder import QuantumEncoder
from quantum.portfolio_quantum import QuantumPortfolio
from quantum.fidelity_matrix import FidelityMatrix
from quantum.fidelity_heatmap import FidelityHeatmap
from quantum.entanglement_matrix import EntanglementMatrix
from quantum.qft_portfolio import QFTPortfolio
from quantum.qpe_portfolio import QPEPortfolio
from quantum.portfolio_optimizer  import PortfolioOptimizer
from quantum.trajectory_portfolio import TrajectoryPortfolio


def run_pipeline(symbols: list[str], days: int) -> dict:
    """
    Run the full pipeline and return a results dict.
    Results are cached in st.session_state under key 'results'.
    """

    results = {}

    with st.spinner("Loading market data..."):
        portfolio = PortfolioAnalyzer(symbols, days)
        portfolio.analyze()
        results["portfolio"] = portfolio

    with st.spinner("Classical analysis..."):
        comparison  = ComparisonEngine(portfolio)
        comparison.print_table()
        correlation = CorrelationEngine(portfolio)
        correlation.build()
        correlation.export_heatmap()
        results["comparison"]  = comparison
        results["correlation"] = correlation

    with st.spinner("Quantum encoding..."):
        quantum_portfolio = QuantumPortfolio(portfolio)
        quantum_portfolio.build()
        results["quantum_portfolio"] = quantum_portfolio

    with st.spinner("Quantum fidelity..."):
        fidelity = FidelityMatrix(quantum_portfolio)
        fidelity.calculate()
        fidelity.export_csv()
        heatmap = FidelityHeatmap(fidelity)
        heatmap.save()
        results["fidelity"] = fidelity

    with st.spinner("Entanglement analysis..."):
        entanglement = EntanglementMatrix(
            quantum_portfolio,
            correlation.correlation
        )
        entanglement.calculate()
        results["entanglement"] = entanglement

    with st.spinner("QFT periodicity..."):
        qft_portfolio = QFTPortfolio(portfolio)
        qft_portfolio.run()
        results["qft_portfolio"] = qft_portfolio

    with st.spinner("Quantum Phase Estimation..."):
        qpe_portfolio = QPEPortfolio(portfolio, quantum_portfolio)
        qpe_portfolio.run()
        results["qpe_portfolio"] = qpe_portfolio

    with st.spinner("VQC Portfolio Optimiser..."):
        port_optimizer = PortfolioOptimizer(portfolio, quantum_portfolio)
        port_optimizer.run()
        results["optimizer"] = port_optimizer.get_optimizer()

    with st.spinner("Quantum Trajectory Engine..."):
        traj_portfolio = TrajectoryPortfolio(portfolio)
        traj_portfolio.run()
        results["traj_portfolio"] = traj_portfolio

    return results

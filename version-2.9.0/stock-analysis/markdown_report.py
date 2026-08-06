"""
markdown_report.py

Generates a professional Markdown report for the
entire portfolio.

Version : 2.9.0
"""

from __future__ import annotations

import os
from datetime import datetime

from config import OUTPUT_REPORT_DIR
from insights import InsightEngine


class MarkdownReport:

    def __init__(
        self,
        portfolio,
        comparison,
        correlation
    ):

        self.portfolio = portfolio
        self.comparison = comparison
        self.correlation = correlation

    # ----------------------------------------------------------

    def build(self):

        lines = []

        #
        # Title
        #

        lines.append("# Quantum Stock Probability Analyzer")
        lines.append("")
        lines.append("## Portfolio Executive Report")
        lines.append("")
        lines.append(
            f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append("")

        #
        # Portfolio Summary
        #

        lines.append("---")
        lines.append("")
        lines.append("## Portfolio Summary")
        lines.append("")

        lines.append(
            f"- Total Stocks : {len(self.portfolio.get_symbols())}"
        )

        best = self.comparison.best_probability()

        lines.append(
            f"- Highest Probability : "
            f"**{best['Symbol']}** "
            f"({best['ProbabilityUp']:.2f}%)"
        )

        risk = self.comparison.lowest_risk()

        lines.append(
            f"- Lowest Volatility : "
            f"**{risk['Symbol']}** "
            f"({risk['Volatility']:.2f})"
        )

        gain = self.comparison.highest_gain()

        lines.append(
            f"- Highest Average Gain : "
            f"**{gain['Symbol']}** "
            f"({gain['AverageGain']:.2f}%)"
        )

        lines.append("")

        #
        # Correlation
        #

        lines.append("---")
        lines.append("")
        lines.append("## Correlation Analysis")
        lines.append("")

        s1, s2, corr = self.correlation.highest_pair()

        lines.append(
            f"- Highest Correlation : "
            f"**{s1} ↔ {s2}** "
            f"({corr:.3f})"
        )

        s1, s2, corr = self.correlation.lowest_pair()

        lines.append(
            f"- Lowest Correlation : "
            f"**{s1} ↔ {s2}** "
            f"({corr:.3f})"
        )

        lines.append("")

        #
        # Individual Stocks
        #

        lines.append("---")
        lines.append("")
        lines.append("## Individual Stock Analysis")
        lines.append("")

        for symbol in self.portfolio.get_symbols():

            analyzer = self.portfolio.get_analyzer(symbol)

            summary = analyzer.get_summary()

            insight = InsightEngine(summary)

            lines.append(f"### {symbol}")
            lines.append("")

            lines.append(
                f"- Trading Days : {summary['TradingDays']}"
            )

            lines.append(
                f"- Green Days : {summary['GreenDays']}"
            )

            lines.append(
                f"- Red Days : {summary['RedDays']}"
            )

            lines.append(
                f"- Probability Up : "
                f"{summary['ProbabilityUp']*100:.2f}%"
            )

            lines.append(
                f"- Average Gain : "
                f"{summary['AverageGain']:.2f}%"
            )

            lines.append(
                f"- Average Loss : "
                f"{summary['AverageLoss']:.2f}%"
            )

            lines.append(
                f"- Volatility : "
                f"{summary['Volatility']:.2f}"
            )

            lines.append(
                f"- Longest Green Streak : "
                f"{summary['LongestGreenStreak']}"
            )

            lines.append(
                f"- Longest Red Streak : "
                f"{summary['LongestRedStreak']}"
            )

            lines.append("")

            lines.append("#### Executive Insight")
            lines.append("")

            for line in insight.executive_summary().split("\n"):

                lines.append(f"> {line}")

            lines.append("")

        #
        # Recommendation
        #

        lines.append("---")
        lines.append("")
        lines.append("## Final Remarks")
        lines.append("")
        lines.append(
            "This report is generated using historical NSE "
            "price statistics and probability analysis."
        )
        lines.append("")
        lines.append(
            "Future versions will include AI-generated "
            "portfolio insights using IBM watsonx and "
            "quantum probability demonstrations using Qiskit."
        )

        return "\n".join(lines)

    # ----------------------------------------------------------

    def export(self):

        os.makedirs(
            OUTPUT_REPORT_DIR,
            exist_ok=True
        )

        filename = os.path.join(
            OUTPUT_REPORT_DIR,
            "Portfolio_Report.md"
        )

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as fp:

            fp.write(
                self.build()
            )

        print()
        print(
            f"Markdown report saved : {filename}"
        )

        return filename

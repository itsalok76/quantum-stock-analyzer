"""
comparison.py

Compares results across a portfolio of stocks.

Version : 2.7.0
"""

from __future__ import annotations

import pandas as pd


class ComparisonEngine:

    def __init__(self, portfolio):

        self.portfolio = portfolio

        self.summary = portfolio.get_all_summaries()

        self.df = self._build_dataframe()

    # ------------------------------------------------------

    def _build_dataframe(self):

        rows = []

        for symbol, s in self.summary.items():

            rows.append({

                "Symbol": symbol,

                "ProbabilityUp":
                    s["ProbabilityUp"] * 100,

                "ProbabilityDown":
                    s["ProbabilityDown"] * 100,

                "AverageGain":
                    s["AverageGain"],

                "AverageLoss":
                    s["AverageLoss"],

                "Volatility":
                    s["Volatility"],

                "GreenDays":
                    s["GreenDays"],

                "RedDays":
                    s["RedDays"]

            })

        return pd.DataFrame(rows)

    # ------------------------------------------------------

    def dataframe(self):

        return self.df

    # ------------------------------------------------------

    def print_table(self):

        print()

        print("=" * 85)

        print("Portfolio Comparison")

        print("=" * 85)

        print(self.df.to_string(index=False))

        print("=" * 85)

    # ------------------------------------------------------

    def rank_probability(self):

        return self.df.sort_values(

            "ProbabilityUp",

            ascending=False

        )

    # ------------------------------------------------------

    def rank_gain(self):

        return self.df.sort_values(

            "AverageGain",

            ascending=False

        )

    # ------------------------------------------------------

    def rank_volatility(self):

        return self.df.sort_values(

            "Volatility"

        )

    # ------------------------------------------------------

    def best_probability(self):

        return self.rank_probability().iloc[0]

    # ------------------------------------------------------

    def highest_gain(self):

        return self.rank_gain().iloc[0]

    # ------------------------------------------------------

    def lowest_risk(self):

        return self.rank_volatility().iloc[0]

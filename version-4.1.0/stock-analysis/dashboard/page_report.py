"""
page_report.py

Dashboard page — Export full Markdown + JSON report.

Version : 4.1.0
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

import streamlit as st

from markdown_report import MarkdownReport
from config import OUTPUT_REPORT_DIR


def render(results: dict):

    st.header("Export Reports")

    st.markdown(
        "Generate and download the **full Markdown report** "
        "(all classical + quantum sections with embedded charts) "
        "and the **portfolio JSON** data file."
    )

    st.divider()

    # ── Build markdown ────────────────────────────────────────────

    if st.button("Generate Full Markdown Report", type="primary"):

        with st.spinner("Building report..."):

            markdown = MarkdownReport(
                results["portfolio"],
                results["comparison"],
                results["correlation"],
                quantum_portfolio   = results.get("quantum_portfolio"),
                fidelity_matrix     = results.get("fidelity"),
                entanglement_matrix = results.get("entanglement"),
                qft_portfolio       = results.get("qft_portfolio"),
                qpe_portfolio       = results.get("qpe_portfolio"),
                optimizer           = results.get("optimizer"),
            )

            md_text  = markdown.build()
            filename = markdown.export()

        st.success(f"Report saved to `{filename}`")

        st.download_button(
            label="Download Portfolio_Report.md",
            data=md_text,
            file_name="Portfolio_Report.md",
            mime="text/markdown",
        )

    st.divider()

    # ── Download optimizer JSON ───────────────────────────────────

    st.subheader("Download Portfolio Optimizer JSON")

    optimizer = results.get("optimizer")
    if optimizer:
        json_str = json.dumps(optimizer.to_dict(), indent=2)
        st.download_button(
            label="Download portfolio_optimizer.json",
            data=json_str,
            file_name="portfolio_optimizer.json",
            mime="application/json",
        )

    st.divider()

    # ── Preview markdown ──────────────────────────────────────────

    st.subheader("Preview — last generated report")

    report_path = Path(OUTPUT_REPORT_DIR) / "Portfolio_Report.md"

    if report_path.exists():
        md_content = report_path.read_text(encoding="utf-8")
        with st.expander("Show Markdown source"):
            st.code(md_content[:3000] + "\n\n... (truncated)", language="markdown")
        st.markdown("---")
        st.markdown(md_content[:5000])
        if len(md_content) > 5000:
            st.info("Preview truncated. Download the full file above.")
    else:
        st.info("No report generated yet. Click the button above.")

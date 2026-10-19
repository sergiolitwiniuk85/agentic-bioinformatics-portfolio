"""LangChain tools that expose the bioinformatics pipeline and its results.

These are the callable tools an LLM agent uses to answer research questions:
inspect datasets, read pipeline summaries, and pull marker genes per cluster.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from langchain_core.tools import tool

REPO = Path(__file__).resolve().parents[3]
DE_CSV = REPO / "results" / "de" / "pbmc3k_markers.csv"
PROV = REPO / "results" / "report" / "provenance.json"
MANIFEST = REPO / "data" / "manifest.json"
XENIUM_MATRIX = REPO / "data" / "xenium" / "cell_feature_matrix.h5"
XENIUM_SUMMARY = REPO / "results" / "xenium" / "xenium_summary.json"

_RUN_HINT = "Run the pipeline first: snakemake -s workflow/Snakefile --directory . --cores 2"


@tool
def list_datasets() -> str:
    """List the available datasets (single-cell, spatial, and subcellular)."""
    parts = []
    if MANIFEST.exists():
        parts.append(MANIFEST.read_text())
    if XENIUM_MATRIX.exists():
        parts.append("xenium: human breast (subcellular), 7275 cells x 280 genes")
    if not parts:
        return f"No datasets prepared yet. {_RUN_HINT}"
    return "\n".join(parts)


@tool
def get_summary() -> str:
    """Return the pipeline summary: number of cells, genes, and clusters."""
    if not PROV.exists():
        return f"No results yet. {_RUN_HINT}"
    return json.dumps(json.loads(PROV.read_text())["summary"], indent=2)


@tool
def get_markers(cluster: str) -> str:
    """Return the top marker genes for one Leiden cluster.

    Args:
        cluster: cluster label as a string, e.g. '0', '3', or '7'.
    """
    if not DE_CSV.exists():
        return f"No DE results yet. {_RUN_HINT}"
    df = pd.read_csv(DE_CSV)
    sub = df[df["group"].astype(str) == str(cluster)]
    if sub.empty:
        return f"No markers found for cluster '{cluster}'."
    return sub[["gene", "logfoldchanges", "pvals_adj"]].head(10).to_string(index=False)


@tool
def get_xenium_summary() -> str:
    """Return the Xenium subcellular analysis summary (cells and clusters)."""
    if not XENIUM_SUMMARY.exists():
        return "No Xenium results yet. Run: snakemake -s workflow/Snakefile --directory . xenium_figure"
    return XENIUM_SUMMARY.read_text()


ALL_TOOLS = [list_datasets, get_summary, get_markers, get_xenium_summary]

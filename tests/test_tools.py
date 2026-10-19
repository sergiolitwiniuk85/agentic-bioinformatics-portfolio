"""Tests for the LangChain tools (no LLM required)."""

import json
from pathlib import Path

import pytest

from agentic_bio.tools import get_markers, get_summary, list_datasets

HAS_RESULTS = Path("results/report/provenance.json").exists()


def test_tool_names():
    names = {t.name for t in [list_datasets, get_summary, get_markers]}
    assert names == {"list_datasets", "get_summary", "get_markers"}


def test_list_datasets_returns_string():
    out = list_datasets.invoke({})
    assert isinstance(out, str) and len(out) > 0


def test_get_summary_returns_string():
    out = get_summary.invoke({})
    assert isinstance(out, str) and len(out) > 0
    if HAS_RESULTS:
        summary = json.loads(out)
        assert summary["n_clusters"] == 8


def test_get_markers_returns_string():
    out = get_markers.invoke({"cluster": "3"})
    assert isinstance(out, str) and len(out) > 0


@pytest.mark.skipif(not HAS_RESULTS, reason="results/ not present — run the pipeline first")
def test_get_markers_cluster_3_b_cells():
    out = get_markers.invoke({"cluster": "3"})
    assert "CD79A" in out

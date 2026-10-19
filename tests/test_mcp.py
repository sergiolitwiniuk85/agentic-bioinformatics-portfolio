"""Tests for the MCP integration (spawns the MCP server over stdio)."""

import pytest

pytest.importorskip("mcp", reason="mcp not installed")

from agentic_bio.mcp.client import call_tool, list_tools


def test_mcp_lists_tools():
    tools = list_tools()
    assert {"submit_job", "job_status", "list_datasets"} <= set(tools)


def test_mcp_list_datasets():
    out = call_tool("list_datasets", {})
    assert "pbmc3k" in out and "visium_sge" in out


def test_mcp_submit_job():
    out = call_tool("submit_job", {"job_name": "qc", "script": "run_qc.sh"})
    assert "job-" in out and "qc" in out

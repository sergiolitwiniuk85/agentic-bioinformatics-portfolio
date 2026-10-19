"""Tests for the LangGraph agent (uses a fake LLM, no API key required)."""

import pytest

langgraph = pytest.importorskip("langgraph", reason="langgraph not installed")
chromadb = pytest.importorskip("chromadb", reason="chromadb not installed")

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from agentic_bio.agent import run_agent
from agentic_bio.rag import ingest_kb


def _fake_llm(*answers: str):
    return GenericFakeChatModel(messages=iter(AIMessage(content=a) for a in answers))


def test_agent_answers_with_grounded_source():
    ingest_kb()
    fake = _fake_llm(
        "Normalize total counts to 10k then log1p, per [02_normalization]."
    )
    result = run_agent(fake, "How should I normalize single-cell RNA-seq data?")
    assert result["answer"]
    assert result["validated"] is True
    assert "[02_normalization]" in result["answer"]


def test_agent_revises_when_ungrounded():
    ingest_kb()
    fake = _fake_llm(
        "Normalization is important.",  # ungrounded -> triggers a revision
        "Normalize counts then log1p, as described in [02_normalization].",  # grounded
    )
    result = run_agent(fake, "How should I normalize single-cell data?")
    assert result["validated"] is True
    assert "[02_normalization]" in result["answer"]
    assert result["revision"] >= 1


def test_agent_runs_mcp_tools_for_dataset_question():
    pytest.importorskip("mcp", reason="mcp not installed")
    ingest_kb()
    fake = _fake_llm("The catalog lists [02_normalization] datasets.")
    result = run_agent(fake, "What datasets are available in the catalog?")
    assert "pbmc3k" in result["tool_output"]

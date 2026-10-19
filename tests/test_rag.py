"""Tests for the RAG layer (requires chromadb + a local embedding model)."""

import pytest

chromadb = pytest.importorskip("chromadb", reason="chromadb not installed")

from agentic_bio.rag import ingest_kb, retrieve


def test_ingest_returns_chunks():
    n = ingest_kb()
    assert n > 0


def test_retrieve_normalization():
    results = retrieve("How should I normalize single-cell RNA-seq data?", k=3)
    assert len(results) > 0
    joined = " ".join(r["text"] for r in results).lower()
    assert any(tok in joined for tok in ("normalize", "normalization", "log1p"))


def test_retrieve_spatial():
    results = retrieve("spatial neighborhood enrichment", k=2)
    assert len(results) > 0
    joined = " ".join(r["text"] for r in results).lower()
    assert "spatial" in joined

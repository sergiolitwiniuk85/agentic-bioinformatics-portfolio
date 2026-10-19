"""RAG: retrieval-augmented generation over the internal knowledge base."""

from agentic_bio.rag.ingest import ingest_kb
from agentic_bio.rag.retrieve import retrieve

__all__ = ["ingest_kb", "retrieve"]

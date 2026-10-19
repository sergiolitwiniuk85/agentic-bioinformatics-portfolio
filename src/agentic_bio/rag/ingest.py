"""Ingest the knowledge base (kb/*.md) into a Chroma vector store."""

from __future__ import annotations

from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

REPO = Path(__file__).resolve().parents[3]
KB_DIR = REPO / "kb"
STORE_DIR = REPO / "data" / "chroma"


def _chunk(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_text(text)


def ingest_kb(kb_dir: Path = KB_DIR, store_dir: Path = STORE_DIR) -> int:
    """Ingest all kb/*.md documents into Chroma. Returns number of chunks stored."""
    import chromadb

    records: list[tuple[str, str]] = []
    for md in sorted(kb_dir.glob("*.md")):
        for chunk in _chunk(md.read_text()):
            records.append((md.stem, chunk))

    client = chromadb.PersistentClient(path=str(store_dir))
    collection = client.get_or_create_collection("knowledge_base")
    collection.upsert(
        ids=[f"{src}:{i}" for i, (src, _) in enumerate(records)],
        documents=[text for _, text in records],
        metadatas=[{"source": src} for src, _ in records],
    )
    return len(records)

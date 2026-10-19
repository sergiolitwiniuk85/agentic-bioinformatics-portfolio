"""Query the knowledge base via Chroma semantic search."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
STORE_DIR = REPO / "data" / "chroma"


def retrieve(query: str, k: int = 3, store_dir: Path = STORE_DIR) -> list[dict]:
    """Return the top-k most relevant chunks (with metadata) for a query."""
    import chromadb

    client = chromadb.PersistentClient(path=str(store_dir))
    collection = client.get_or_create_collection("knowledge_base")
    result = collection.query(query_texts=[query], n_results=k)

    out = []
    for i in range(len(result["ids"][0])):
        out.append(
            {
                "id": result["ids"][0][i],
                "source": result["metadatas"][0][i]["source"],
                "text": result["documents"][0][i],
            }
        )
    return out

"""E02 eval gate: agent + RAG quality.

Metrics:
  - RAG top-1 hit rate (does retrieval rank the right doc first?)
  - grounding (did the answer cite a real source?)
  - hallucinated citations (citations to non-existent sources)
  - task success (keyword proxy for correctness)
  - privacy (no PII / raw cell barcodes)

Run:
    python evals/e02_agent.py                 # fake LLM (no key)
    python evals/e02_agent.py --llm opencode-go
    python evals/e02_agent.py --llm ollama
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ALL_SOURCES = {"01_qc", "02_normalization", "03_clustering", "04_spatial"}

BENCHMARK = [
    {
        "question": "How should I normalize single-cell RNA-seq data?",
        "expected_source": "02_normalization",
        "keywords": ["normalize", "log1p", "counts"],
    },
    {
        "question": "What quality control steps filter single-cell cells?",
        "expected_source": "01_qc",
        "keywords": ["filter", "mitochondrial", "genes"],
    },
    {
        "question": "How does clustering group cells by similarity?",
        "expected_source": "03_clustering",
        "keywords": ["leiden", "pca", "neighbors", "cluster"],
    },
    {
        "question": "How is spatial transcriptomics analyzed?",
        "expected_source": "04_spatial",
        "keywords": ["spatial", "neighborhood", "enrichment"],
    },
]

PII_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"AAAC[A-Z0-9-]{12,}"),
]


def rag_hit_rate() -> float:
    from agentic_bio.rag import ingest_kb, retrieve

    ingest_kb()
    hits = 0
    for b in BENCHMARK:
        docs = retrieve(b["question"], k=1)
        top = docs[0]["source"] if docs else None
        ok = top == b["expected_source"]
        hits += ok
        print(f"  [{b['expected_source']:<16}] -> got {top} {'OK' if ok else 'MISS'}")
    rate = hits / len(BENCHMARK)
    print(f"  RAG top-1 hit rate: {hits}/{len(BENCHMARK)} ({rate:.0%})")
    return rate


def agent_metrics(llm) -> dict:
    from agentic_bio.agent import run_agent

    grounded = 0
    success = 0
    hallucinated = 0
    pii = 0
    for b in BENCHMARK:
        state = run_agent(llm, b["question"])
        answer = state["answer"]
        cited = set(re.findall(r"\[([A-Za-z0-9_]+)\]", answer))
        if cited & ALL_SOURCES:
            grounded += 1
        hallucinated += len(cited - ALL_SOURCES)
        if any(k in answer.lower() for k in b["keywords"]):
            success += 1
        for p in PII_PATTERNS:
            if p.search(answer):
                pii += 1
    return {
        "grounded": grounded,
        "task_success": success,
        "hallucinated_citations": hallucinated,
        "pii": pii,
        "total": len(BENCHMARK),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", default="fake", choices=["fake", "opencode-go", "ollama"])
    args = ap.parse_args()

    print("=== E02 eval gate ===\n")

    print("1) RAG retrieval")
    rag = rag_hit_rate()

    print(f"\n2) Agent (llm={args.llm})")
    from agentic_bio.agent.llm import get_llm

    llm = get_llm(args.llm)
    m = agent_metrics(llm)
    print(f"  grounded:            {m['grounded']}/{m['total']}")
    print(f"  task success (kw):   {m['task_success']}/{m['total']}")
    print(f"  hallucinated cites:  {m['hallucinated_citations']}")
    print(f"  PII leaks:           {m['pii']}")

    passed = rag >= 0.75 and m["grounded"] >= m["total"] * 0.5 and m["pii"] == 0
    print(f"\n=== RESULT: {'PASS' if passed else 'FAIL'} ===")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

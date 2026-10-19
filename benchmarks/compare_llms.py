"""Benchmark: same agent tasks on hosted (opencode-go) vs local (Ollama) models.

Run:  python benchmarks/compare_llms.py
Out:  benchmarks/results.json + a markdown table on stdout.

No API keys are stored in this repo — the LLM factory reads them from the
OPENCODE_API_KEY env var or the opencode auth file (~/.local/share/opencode/auth.json).
"""

import json
import time
from pathlib import Path

from agentic_bio.agent import get_llm, run_agent
from agentic_bio.rag import ingest_kb

QUESTIONS = [
    "How should I normalize single-cell RNA-seq data?",
    "What quality control steps are needed for single-cell data?",
    "How does clustering group cells by transcriptional similarity?",
]

MODELS = [
    ("opencode-go", "deepseek-v4.1-flash", "hosted"),
    ("ollama", "llama3.2:1b", "local"),
    ("ollama", "qwen2.5:7b", "local"),
]

RESULTS = Path(__file__).resolve().parent / "results.json"


def main() -> None:
    ingest_kb()
    rows = []
    for provider, model, kind in MODELS:
        llm = get_llm(provider, model=model)
        for question in QUESTIONS:
            t0 = time.perf_counter()
            state = run_agent(llm, question)
            elapsed = time.perf_counter() - t0
            rows.append(
                {
                    "model": f"{provider}/{model}",
                    "kind": kind,
                    "question": question,
                    "latency_s": round(elapsed, 2),
                    "revisions": state["revision"],
                    "validated": state["validated"],
                    "answer": state["answer"],
                }
            )
    RESULTS.write_text(json.dumps(rows, indent=2))
    _print_markdown(rows)


def _print_markdown(rows: list[dict]) -> None:
    by_model: dict[str, list[dict]] = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r)

    print("\n| Model | Type | Avg latency | Grounded |")
    print("| --- | --- | --- | --- |")
    for model, rs in by_model.items():
        avg = sum(r["latency_s"] for r in rs) / len(rs)
        grounded = sum(1 for r in rs if r["validated"])
        print(f"| {model} | {rs[0]['kind']} | {avg:.2f}s | {grounded}/{len(rs)} |")


if __name__ == "__main__":
    main()

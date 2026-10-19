# 🧬 Agentic Bioinformatics Assistant

> **An LLM-powered research assistant for single-cell & spatial omics.**
> Built with LangChain/LangGraph, reproducible pipelines, and continuous evaluation — from code to rendered diagrams.

[![CI](https://github.com/sergiolitwiniuk85/agentic-bioinformatics-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/sergiolitwiniuk85/agentic-bioinformatics-portfolio/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is this?

A portfolio project that proves **end-to-end agentic bioinformatics**: an AI agent that takes a research question, plans it, retrieves *grounded* context (RAG), runs real single-cell / spatial analyses through typed tools, **validates its own output**, and answers with citations — all wrapped in reproducible CI/CD.

The diagrams on this page are **written as Mermaid code and rendered directly by GitHub**. Change the code, the diagram updates.

---

## Architecture

```mermaid
flowchart LR
    U["🧑‍🔬 Researcher"] -->|"question"| A["🤖 Agent<br/>(LangGraph)"]
    A -->|"plan"| R["📚 RAG Retriever"]
    A -->|"tool call"| T["🔧 Analysis Tools"]
    A -->|"tool call"| M["🔌 MCP Server<br/>(HPC / DB)"]
    T --> P["⚙️ Snakemake Pipeline"]
    P --> D[("🗂️ Datasets<br/>scRNA-seq + spatial")]
    R --> K[("🧠 Vector Store")]
    A -->|"validated + cited answer"| U
```

## Agent workflow (state machine)

```mermaid
stateDiagram-v2
    [*] --> Plan
    Plan --> Retrieve : needs context
    Plan --> RunAnalysis : needs compute
    Retrieve --> Validate
    RunAnalysis --> Validate
    Validate --> Answer : passed
    Validate --> Plan : revise (max 2)
    Answer --> [*]
```

## CI / evaluation pipeline

```mermaid
flowchart LR
    P["Push / PR"] --> L["🧹 Lint + Format"]
    L --> T["🧪 Unit Tests"]
    T --> E["📊 Eval Harness"]
    E --> B["🐳 Docker Build"]
    B --> A["📦 Artifacts + Report"]
```

---

## ✨ Features

- 🧠 **Agentic workflow** (LangGraph) — `plan → retrieve → run → validate → answer`
- 📚 **RAG** over protocols & literature with **citation-aware** answers
- 🔧 **Tool calling** — run analyses, query results, list datasets (typed schemas)
- 🔌 **MCP integration** for HPC / database resources
- 🧬 **Real omics** — single-cell RNA-seq, spatial transcriptomics, perturbational
- ⚙️ **Reproducible** Snakemake pipeline with provenance logs
- 📊 **Continuous evaluation** — correctness, reproducibility, RAG faithfulness, privacy
- 🐳 **CI/CD** — GitHub Actions + Docker

---

## 🧰 Tech stack

| Layer | Tools |
| --- | --- |
| LLM + agents | LangChain, LangGraph |
| RAG | Chroma |
| Omics | scanpy, anndata, squidpy, decoupler |
| Workflow | Snakemake |
| CI/CD | GitHub Actions, Docker |
| Packaging | uv + pyproject.toml |

---

## 🚀 Quickstart

```bash
git clone https://github.com/sergiolitwiniuk85/agentic-bioinformatics-portfolio.git
cd agentic-bioinformatics-portfolio

# core package (light)
pip install -e . pytest ruff

# full agent + omics stack (heavy, optional)
# uv sync --extra agent --extra omics

pytest -q
```

---

## ⚙️ Reproducible pipeline

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install snakemake decoupler pyyaml matplotlib

# full workflow: download → QC → normalize → cluster → DE → spatial → perturbation
snakemake -s workflow/Snakefile --directory . --cores 2

# eval gate (correctness / reproducibility / privacy)
python evals/e01_pipeline.py
```

**E01 result** (PBMC 3k, 8 clusters):

| Check | Result |
| --- | --- |
| Correctness (expected markers) | ✅ 14/16 found (CD79A, LYZ, NKG7, PPBP, …) |
| Reproducibility (artifact hashes) | ✅ match |
| Privacy (no PII / raw IDs) | ✅ clean |

### Example run — two datasets, two analyses

The pipeline runs on **two independent datasets**:

**1. PBMC 3k — single-cell RNA-seq (blood).** Leiden recovers the classic **8 cell types**:

| Cluster | Cell type | Markers |
| --- | --- | --- |
| 0 | T cells | LTB, IL32 |
| 1 | Ribosomal / technical | RPS12, RPL32 |
| 2 | NK / cytotoxic | NKG7, GZMA |
| 3 | B cells | CD79A, MS4A1 |
| 4 | Monocytes | LYZ, S100A8 |
| 5 | Monocytes / DC | AIF1, LST1 |
| 6 | Dendritic cells | HLA-DPA1, HLA-DPB1 |
| 7 | Megakaryocytes | PPBP, PF4 |

**UMAP** (PBMC 3k, 8 clusters):

![UMAP](docs/figures/umap_leiden.png)

**2. Visium lymph node — spatial transcriptomics (tissue).** A *different* sample (4,035 spots). Leiden discovers **11 spatial niches** here, not 8 — the tissue has more cell states and spatial structure than circulating blood. Cluster labels are local to each dataset: Visium cluster "3" is unrelated to PBMC cluster "3".

**Spatial tissue map** (Visium lymph node, 11 clusters over H&E):

![Spatial clusters](docs/figures/spatial_leiden.png)

**Spatial gene expression** (Visium lymph node, `MS4A1` — B cells):

![Spatial MS4A1](docs/figures/spatial_gene.png)

---

## 🧠 RAG (retrieval-augmented generation)

The agent grounds its answers in an internal knowledge base (`kb/*.md`) via Chroma:

```bash
pip install chromadb

# ingest the knowledge base into a local vector store
python -c "from agentic_bio.rag import ingest_kb; print(ingest_kb(), 'chunks')"

# retrieve the most relevant context for a question
python -c "from agentic_bio.rag import retrieve; print(retrieve('how to normalize single-cell data?', k=2))"
```

---

## 🤖 LangGraph agent

The agent orchestrates `retrieve → run tools → answer → validate` as a bounded loop — if the answer isn't grounded in a retrieved source, it re-answers (max 2 revisions):

```bash
pip install langgraph

python -c "
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from agentic_bio.agent import run_agent
from agentic_bio.rag import ingest_kb

ingest_kb()
fake = GenericFakeChatModel(messages=iter([
    AIMessage(content='Normalize total counts to 10k then log1p, per [02_normalization].')
]))
print(run_agent(fake, 'How should I normalize single-cell data?')['answer'])
"
```

The LLM is **pluggable** — pass any `BaseChatModel` (OpenAI-compatible endpoint, Ollama, etc.) to `build_agent(llm)`.

---

## ⚡ LLM benchmark (hosted vs local)

The same agent tasks run on a hosted model vs two local open-weight models. **No API keys are stored in this repo** — the factory reads them from the `OPENCODE_API_KEY` env var or the opencode auth file:

| Model | Type | Avg latency | Grounded |
| --- | --- | --- | --- |
| opencode-go `deepseek-v4.1-flash` | ☁️ hosted | 4.2s | 3/3 |
| ollama `llama3.2:1b` (1.3 GB) | 💻 local | 41s | 2/3 |
| ollama `qwen2.5:7b` (4.7 GB) | 💻 local | 64s | 2/3 |

> **Hardware note** (for comparison only): the local Ollama models ran on **CPU-only** inference — an ASUS VivoBook X515EAU (Intel Core i5-1135G7, 19 GB RAM, integrated Intel Iris Xe graphics, **no dedicated GPU**). A machine with a dedicated GPU would run the local models significantly faster.

> **Grounded** = the answer cited a retrieved source (`[name]`). All three answered *correctly*; the hosted model reliably cited its sources, while the local models often answered correctly *without* citing. Local models trade speed for privacy and offline use.

Reproduce locally:

```bash
python benchmarks/compare_llms.py
```

---

## 📁 Project structure

```
.
├── .github/workflows/ci.yml   # CI pipeline (lint → test)
├── src/agentic_bio/           # package source (data, tools, rag, agent)
├── kb/                        # knowledge base for RAG
├── workflow/                  # Snakemake pipeline + scripts + config
├── evals/                     # eval gates (E01 …)
├── benchmarks/                # LLM comparison harness
├── tests/                     # unit + smoke + RAG + agent tests
├── docs/                      # architecture & Mermaid diagrams + figures
├── pyproject.toml             # project config + dependencies
├── LICENSE
└── README.md
```

---

## 🗺️ Roadmap

| Version | Scope |
| --- | --- |
| v0.1 (beta) | scaffold, CI, architecture ✅ |
| v0.2 | data fixtures + Snakemake pipeline ✅ |
| v0.3 | LangChain tools + RAG ✅ |
| v0.4 | LangGraph agent + MCP — *in progress* |
| v0.5 | eval harness + benchmark |
| v1.0 | docs, demo, workshop |

---

## 📜 License

[MIT](LICENSE)

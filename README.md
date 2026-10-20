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

### Example run — three datasets, three analyses

The pipeline runs on **three independent datasets**:

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

**3. Xenium breast cancer — single-cell resolution.** Each dot is one segmented cell (7,248 cells), not a spot. Cells are consolidated into **7 major cell types** (from 14 clusters) by marker-gene scoring, then tissue borders are validated with neighborhood enrichment:

![Xenium cell types](docs/figures/xenium_cell_types.png)

> Epithelial/tumor 41% · Fibroblast/CAF 19% · B cells 13% · Myeloid 12% · T cells 8% · Endothelial 5% · NK 3%.

**E03 result**: integrity ✅, single-cell coordinates ✅, reproducibility ✅. Xenium data is a manual download (~379 MB): `curl -O https://cf.10xgenomics.com/samples/xenium/2.0.0/Xenium_V1_human_Breast_2fov/Xenium_V1_human_Breast_2fov_outs.zip`, then `snakemake -s workflow/Snakefile --directory . xenium_figure`.

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

## 🔌 MCP integration (HPC + datasets)

The agent can call external resources through the **Model Context Protocol** — the same pattern used to wire a real cluster or database. A simulated server exposes:

| Tool | Purpose |
| --- | --- |
| `submit_job` | submit an analysis job to the (simulated) HPC |
| `job_status` | check a job's status |
| `list_datasets` | list the internal dataset catalog |

```bash
python -m agentic_bio.mcp.server    # start the MCP server (stdio)

python -c "
from agentic_bio.mcp.client import call_tool
print(call_tool('list_datasets', {}))
print(call_tool('submit_job', {'job_name': 'qc', 'script': 'run_qc.sh'}))
"
```

The agent routes questions about *datasets*, *jobs*, or *HPC* to these MCP tools automatically.

---

## 📊 E02 — agent eval gate

The agent is evaluated on a 4-question benchmark (RAG retrieval + answer quality), run here with the hosted model:

| Metric | Result |
| --- | --- |
| RAG top-1 hit rate | 4/4 (100%) |
| Grounded (cited a real source) | 4/4 |
| Task success (keyword) | 4/4 |
| Hallucinated citations | 0 |
| Privacy (no PII) | ✅ |

```bash
python evals/e02_agent.py --llm opencode-go   # or --llm ollama / default fake
```

---

## 🔬 In silico interaction & signature filters

A **virtual microscope**: apply a filter to reveal a class of cell-cell interaction, or a functional gene signature, over the tissue.

- **7 spatial-interaction filters**: neighborhood enrichment, tissue borders, paracrine distance, immune TLS, juxtacrine (direct cell contact), niche domains, ECM-cell.
- **10 pre-indexed gene-signature panels**: proliferation, hypoxia, EMT, interferon, apoptosis, angiogenesis, immunotherapy/checkpoint, ER signaling, HER2, stemness.

```python
from agentic_bio.interactions import analyze_interaction, score_signature, plot_interaction, plot_signature
from agentic_bio.data.xenium import load_xenium, analyze_xenium, annotate_cell_types

adata = annotate_cell_types(analyze_xenium(load_xenium()))
adata, _ = analyze_interaction(adata, "juxtacrine")     # direct cell contact (Xenium-only)
adata, _ = score_signature(adata, "checkpoint")         # PD-L1 / PD-1 signature
plot_interaction(adata, "juxtacrine", "juxtacrine.png")
plot_signature(adata, "checkpoint", "checkpoint.png")
```

| Juxtacrine (direct contact) | Immunotherapy / checkpoint |
| --- | --- |
| ![Juxtacrine](docs/figures/interaction_juxtacrine.png) | ![Checkpoint](docs/figures/signature_checkpoint.png) |

---

### 🔬 Full Xenium analysis (50k cells, breast full) — **v0.7**

The pipeline now supports the **full breast Xenium dataset** (167,780 cells) with a **50k cell subset** for a reproducible, strong example:

```bash
# download breast full (~9.86 GB)
curl -O https://cf.10xgenomics.com/samples/xenium/1.0.1/Xenium_FFPE_Human_Breast_Cancer_Rep1/Xenium_FFPE_Human_Breast_Cancer_Rep1_outs.zip

# run full pipeline on 50k cells + all filters × 3 thresholds
snakemake -s workflow/Snakefile --directory . xenium_figure
# or run the full script directly:
python workflow/scripts/xenium_full.py --data /path/to/outs --n-cells 50000 --out results/xenium_full
```

**All filters × 3 thresholds generated:**

| Filter | Type | Thresholds | Plots |
|---|---|---|---|
| neighborhood_enrichment | interaction | — | 1 |
| tissue_borders | interaction | — | 1 |
| paracrine_distance | interaction | 3 (75/90/95% pct) | 3 |
| immune_tls | interaction | 3 (30/50/80 µm) | 3 |
| juxtacrine | interaction | — | 1 |
| niche | interaction | — | 1 |
| checkpoint | signature | 3 (p50/p75/p90) | 3 |
| er_signaling | signature | 3 (p50/p75/p90) | 3 |
| proliferation | signature | 3 (p50/p75/p90) | 3 |
| angiogenesis | signature | 3 (p50/p75/p90) | 3 |
| emt | signature | 3 (p50/p75/p90) | 3 |
| interferon | signature | skipped (0 genes in panel) | — |
| apoptosis | signature | skipped (0 genes in panel) | — |
| hypoxia | signature | skipped (0 genes in panel) | — |
| stemness | signature | skipped (0 genes in panel) | — |

**Figures generated (click a thumbnail to open full size):**

| Preview | Figure | Description |
|---|---|---|
| [![cell types](docs/figures/xenium_cell_types.png)](docs/figures/xenium_cell_types.png) | `xenium_cell_types.png` | 7 cell types, 7,248 cells |
| [![subcellular](docs/figures/xenium_subcellular.png)](docs/figures/xenium_subcellular.png) | `xenium_subcellular.png` | original 14-cluster map |
| [![neighborhood](docs/figures/interaction_neighborhood_enrichment.png)](docs/figures/interaction_neighborhood_enrichment.png) | `interaction_neighborhood_enrichment.png` | neighborhood enrichment heatmap |
| [![borders](docs/figures/interaction_tissue_borders.png)](docs/figures/interaction_tissue_borders.png) | `interaction_tissue_borders.png` | tissue interface score |
| [![niche](docs/figures/interaction_niche.png)](docs/figures/interaction_niche.png) | `interaction_niche.png` | niche domains |
| [![juxtacrine](docs/figures/interaction_juxtacrine.png)](docs/figures/interaction_juxtacrine.png) | `interaction_juxtacrine.png` | direct cell contacts |
| [![paracrine t75](docs/figures/interaction_paracrine_t75.png)](docs/figures/interaction_paracrine_t75.png) | `interaction_paracrine_t75.png` | paracrine distance, p75 |
| [![paracrine t90](docs/figures/interaction_paracrine_t90.png)](docs/figures/interaction_paracrine_t90.png) | `interaction_paracrine_t90.png` | paracrine distance, p90 |
| [![paracrine t95](docs/figures/interaction_paracrine_t95.png)](docs/figures/interaction_paracrine_t95.png) | `interaction_paracrine_t95.png` | paracrine distance, p95 |
| [![TLS r30](docs/figures/interaction_immune_tls_r30.png)](docs/figures/interaction_immune_tls_r30.png) | `interaction_immune_tls_r30.png` | immune TLS, r30 µm |
| [![TLS r50](docs/figures/interaction_immune_tls_r50.png)](docs/figures/interaction_immune_tls_r50.png) | `interaction_immune_tls_r50.png` | immune TLS, r50 µm |
| [![TLS r80](docs/figures/interaction_immune_tls_r80.png)](docs/figures/interaction_immune_tls_r80.png) | `interaction_immune_tls_r80.png` | immune TLS, r80 µm |
| [![checkpoint p50](docs/figures/signature_checkpoint_p50.png)](docs/figures/signature_checkpoint_p50.png) | `signature_checkpoint_p50.png` | checkpoint signature, p50 |
| [![checkpoint p75](docs/figures/signature_checkpoint_p75.png)](docs/figures/signature_checkpoint_p75.png) | `signature_checkpoint_p75.png` | checkpoint signature, p75 |
| [![checkpoint p90](docs/figures/signature_checkpoint_p90.png)](docs/figures/signature_checkpoint_p90.png) | `signature_checkpoint_p90.png` | checkpoint signature, p90 |
| [![ER p50](docs/figures/signature_er_signaling_p50.png)](docs/figures/signature_er_signaling_p50.png) | `signature_er_signaling_p50.png` | ER signaling, p50 |
| [![ER p75](docs/figures/signature_er_signaling_p75.png)](docs/figures/signature_er_signaling_p75.png) | `signature_er_signaling_p75.png` | ER signaling, p75 |
| [![ER p90](docs/figures/signature_er_signaling_p90.png)](docs/figures/signature_er_signaling_p90.png) | `signature_er_signaling_p90.png` | ER signaling, p90 |
| [![prolif p50](docs/figures/signature_proliferation_p50.png)](docs/figures/signature_proliferation_p50.png) | `signature_proliferation_p50.png` | proliferation, p50 |
| [![prolif p75](docs/figures/signature_proliferation_p75.png)](docs/figures/signature_proliferation_p75.png) | `signature_proliferation_p75.png` | proliferation, p75 |
| [![prolif p90](docs/figures/signature_proliferation_p90.png)](docs/figures/signature_proliferation_p90.png) | `signature_proliferation_p90.png` | proliferation, p90 |
| [![angio p50](docs/figures/signature_angiogenesis_p50.png)](docs/figures/signature_angiogenesis_p50.png) | `signature_angiogenesis_p50.png` | angiogenesis, p50 |
| [![angio p75](docs/figures/signature_angiogenesis_p75.png)](docs/figures/signature_angiogenesis_p75.png) | `signature_angiogenesis_p75.png` | angiogenesis, p75 |
| [![angio p90](docs/figures/signature_angiogenesis_p90.png)](docs/figures/signature_angiogenesis_p90.png) | `signature_angiogenesis_p90.png` | angiogenesis, p90 |
| [![EMT p50](docs/figures/signature_emt_p50.png)](docs/figures/signature_emt_p50.png) | `signature_emt_p50.png` | EMT, p50 |
| [![EMT p75](docs/figures/signature_emt_p75.png)](docs/figures/signature_emt_p75.png) | `signature_emt_p75.png` | EMT, p75 |
| [![EMT p90](docs/figures/signature_emt_p90.png)](docs/figures/signature_emt_p90.png) | `signature_emt_p90.png` | EMT, p90 |

**E03 result** (Xenium): integrity ✅, single-cell coordinates ✅, reproducibility ✅.  
**Benchmark (50k cells):** `opencode-go/deepseek-v4.1-flash` 4.2s / `ollama llama3.2:1b` 41s / `ollama qwen2.5:7b` 64s.

> Xenium data (2-FOV): `curl -O https://cf.10xgenomics.com/samples/xenium/2.0.0/Xenium_V1_human_Breast_2fov/Xenium_V1_human_Breast_2fov_outs.zip` (379 MB).  
> **Full breast (167k cells):** `curl -O https://cf.10xgenomics.com/samples/xenium/1.0.1/Xenium_FFPE_Human_Breast_Cancer_Rep1/Xenium_FFPE_Human_Breast_Cancer_Rep1_outs.zip` (~9.86 GB). Subset to 50k: `snakemake -s workflow/Snakefile --directory . xenium_figure --n-cells 50000`.

---

## 📁 Project structure

```
.
├── .github/workflows/ci.yml   # CI pipeline (lint → test)
├── src/agentic_bio/           # package source (data, tools, rag, agent, mcp)
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
| v0.4 | LangGraph agent + MCP ✅ |
| v0.5 | eval harness + benchmark ✅ |
| v0.6 | Xenium spatial example (subcellular) ✅ |
| v1.0 | docs, demo, workshop — *next* |

---

## 📜 License

[MIT](LICENSE)

# Architecture

Diagrams are authored as **Mermaid** and rendered directly by GitHub — edit the code, the diagram updates.

## System architecture

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

## Agent state machine

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

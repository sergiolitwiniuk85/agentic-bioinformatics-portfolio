"""LangGraph agent: retrieve -> run tools -> answer -> validate (bounded loop).

The agent is LLM-agnostic: any LangChain ``BaseChatModel`` can be injected.
Use a fake LLM for deterministic tests, or a real one (OpenAI-compatible,
Ollama, etc.) for live use.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

MAX_REVISIONS = 2

SYSTEM_PROMPT = (
    "You are a bioinformatics research assistant. Answer using ONLY the retrieved "
    "context and tool results provided. Cite the source document as [<name>] when you "
    "use it. If the information is insufficient, say so clearly."
)


class AgentState(TypedDict):
    question: str
    context: str
    tool_output: str
    answer: str
    revision: int
    validated: bool


def _retrieve(state: AgentState) -> dict:
    from agentic_bio.rag import retrieve

    docs = retrieve(state["question"], k=3)
    context = "\n\n".join(f"[{d['source']}] {d['text']}" for d in docs)
    return {"context": context}


def _run_tools(state: AgentState) -> dict:
    from agentic_bio.tools import get_markers, get_summary

    parts = [f"Pipeline summary:\n{get_summary.invoke({})}"]
    m = re.search(r"cluster\s+(\d+)", state["question"].lower())
    if m:
        cluster = m.group(1)
        parts.append(
            f"Markers for cluster {cluster}:\n{get_markers.invoke({'cluster': cluster})}"
        )
    return {"tool_output": "\n\n".join(parts)}


def _answer(llm) -> Callable[[AgentState], dict]:
    def node(state: AgentState) -> dict:
        prompt = (
            f"Question: {state['question']}\n\n"
            f"Retrieved context:\n{state['context']}\n\n"
            f"Tool results:\n{state['tool_output']}\n\n"
            "Answer (cite sources as [<name>]):"
        )
        resp = llm.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
        )
        return {"answer": resp.content}

    return node


def _validate(state: AgentState) -> dict:
    sources = set(re.findall(r"\[(\d+_[a-z]+)\]", state["context"]))
    cited = set(re.findall(r"\[(\d+_[a-z]+)\]", state["answer"]))
    grounded = bool(sources & cited)
    return {"validated": grounded, "revision": state["revision"] + 1}


def _should_continue(state: AgentState) -> str:
    if state["validated"] or state["revision"] >= MAX_REVISIONS:
        return "end"
    return "revise"


def build_agent(llm) -> Any:
    g = StateGraph(AgentState)
    g.add_node("retrieve", _retrieve)
    g.add_node("run_tools", _run_tools)
    g.add_node("answer", _answer(llm))
    g.add_node("validate", _validate)

    g.add_edge(START, "retrieve")
    g.add_edge("retrieve", "run_tools")
    g.add_edge("run_tools", "answer")
    g.add_edge("answer", "validate")
    g.add_conditional_edges(
        "validate",
        _should_continue,
        {"end": END, "revise": "answer"},
    )
    return g.compile()


def run_agent(llm, question: str) -> dict:
    """Run the agent on a question and return the final state."""
    app = build_agent(llm)
    return app.invoke(
        {
            "question": question,
            "context": "",
            "tool_output": "",
            "answer": "",
            "revision": 0,
            "validated": False,
        }
    )

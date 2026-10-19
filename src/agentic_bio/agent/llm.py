"""LLM factory: opencode-go (hosted) or Ollama (local), with a fake fallback.

Usage:
    from agentic_bio.agent.llm import get_llm

    llm = get_llm("opencode-go")      # reuse the opencode-go subscription key
    llm = get_llm("ollama")           # local open-weight model (http://localhost:11434)
    llm = get_llm("fake")             # deterministic, no key (for tests/demo)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

OPENCODE_BASE_URL = "https://opencode.ai/zen/go/v1"
OPENCODE_DEFAULT_MODEL = "deepseek-v4.1-flash"

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_DEFAULT_MODEL = "llama3.2:1b"


def _opencode_key() -> str | None:
    """Return the opencode-go API key from env, or the opencode auth file."""
    key = os.environ.get("OPENCODE_API_KEY")
    if key:
        return key
    auth = Path.home() / ".local/share/opencode/auth.json"
    if auth.exists():
        try:
            return json.loads(auth.read_text())["opencode-go"]["key"]
        except (KeyError, json.JSONDecodeError):
            return None
    return None


def get_llm(provider: str = "opencode-go", model: str | None = None, **kwargs):
    """Build a LangChain chat model for the given provider.

    provider: "opencode-go" (default), "ollama", or "fake".
    """
    if provider == "fake":
        from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
        from langchain_core.messages import AIMessage

        return GenericFakeChatModel(
            messages=iter(
                [AIMessage(content="[02_normalization] Normalize counts, then log1p.")]
            )
        )

    from langchain_openai import ChatOpenAI

    if provider == "ollama":
        return ChatOpenAI(
            base_url=os.environ.get("OLLAMA_BASE_URL", OLLAMA_BASE_URL),
            api_key="ollama",
            model=model or OLLAMA_DEFAULT_MODEL,
            **kwargs,
        )

    # opencode-go
    key = _opencode_key()
    if not key:
        raise ValueError(
            "No opencode-go key found. Set OPENCODE_API_KEY or run `opencode auth login`."
        )
    return ChatOpenAI(
        base_url=OPENCODE_BASE_URL,
        api_key=key,
        model=model or OPENCODE_DEFAULT_MODEL,
        default_headers={"x-opencode-session": "agentic-bio"},
        **kwargs,
    )

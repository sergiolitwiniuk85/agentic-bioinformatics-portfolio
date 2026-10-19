"""Synchronous client for the MCP server (stdio transport)."""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command=sys.executable, args=["-m", "agentic_bio.mcp.server"]
)


async def _list_tools_async() -> list[str]:
    async with stdio_client(SERVER) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        result = await session.list_tools()
        return [t.name for t in result.tools]


async def _call_tool_async(name: str, args: dict[str, Any]) -> str:
    async with stdio_client(SERVER) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool(name, args)
        return "".join(
            c.text for c in result.content if getattr(c, "text", None) is not None
        )


def list_tools() -> list[str]:
    """Return the names of the tools exposed by the MCP server."""
    return asyncio.run(_list_tools_async())


def call_tool(name: str, args: dict[str, Any] | None = None) -> str:
    """Synchronously call an MCP tool and return its text output.

    Retries once because the stdio subprocess can race on teardown.
    """
    args = args or {}
    last_exc: Exception | None = None
    for _ in range(2):
        try:
            return asyncio.run(_call_tool_async(name, args))
        except RuntimeError as exc:
            last_exc = exc
    raise last_exc if last_exc is not None else RuntimeError("MCP call failed")

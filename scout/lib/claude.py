"""Thin wrapper around the Anthropic SDK for the Ventrix scout agents."""
import json
import os
from typing import Any, Dict, List, Optional

from anthropic import Anthropic

CHEAP_MODEL = "claude-haiku-4-5"      # research / scraping passes
SMART_MODEL = "claude-sonnet-4-6"     # synthesis / final write-up


def client() -> Anthropic:
    """Return an authenticated Anthropic client."""
    return Anthropic()  # reads ANTHROPIC_API_KEY from env


def run_agent(
    *,
    system: str,
    user: str,
    model: str = SMART_MODEL,
    enable_web_search: bool = True,
    max_tokens: int = 4096,
    max_web_searches: int = 6,
) -> str:
    """Run a single-turn agent with optional web search.

    Returns the agent's final text output (the last assistant text block).
    """
    c = client()
    tools = []
    if enable_web_search:
        tools.append({
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": max_web_searches,
        })
    msg = c.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        tools=tools if tools else [],
    )
    # Collect all assistant text blocks
    chunks: List[str] = []
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            chunks.append(block.text)
    return "\n".join(chunks).strip()


def parse_json_or_fallback(text: str, fallback: Any) -> Any:
    """Try to extract JSON from a model response. Return `fallback` if it fails."""
    # Look for the largest JSON object/array in the text
    candidates = []
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        depth = 0
        start_idx: Optional[int] = None
        for i, ch in enumerate(text):
            if ch == start_char:
                if depth == 0:
                    start_idx = i
                depth += 1
            elif ch == end_char and depth > 0:
                depth -= 1
                if depth == 0 and start_idx is not None:
                    candidates.append(text[start_idx : i + 1])
                    start_idx = None
    candidates.sort(key=len, reverse=True)
    for snippet in candidates:
        try:
            return json.loads(snippet)
        except Exception:
            continue
    return fallback

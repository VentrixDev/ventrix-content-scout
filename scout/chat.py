"""Blake's interactive chat agent.

Loads the latest weekly brief + intel + verified prospects and lets Blake ask
questions in natural language. Powered by Claude Sonnet with web search.

Usage:
    python -m scout.chat
"""
import datetime
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from anthropic import Anthropic  # noqa: E402


ROOT = Path(__file__).parent.parent
BRIEFS = ROOT / "briefs"
PROSPECTS = BRIEFS / "prospects"
INTEL = BRIEFS / "intel"


def latest_file(folder: Path, pattern: str) -> Path | None:
    files = sorted(folder.glob(pattern), reverse=True)
    return files[0] if files else None


def load_context() -> str:
    """Pack the latest brief + prospects + intel into one context blob."""
    parts = []
    brief = latest_file(BRIEFS, "week-of-*.md")
    if brief:
        parts.append(f"# This week's Ventrix content brief ({brief.name})\n\n{brief.read_text()}")

    verified = latest_file(PROSPECTS, "*-verified.csv")
    if verified:
        parts.append(f"# Verified salesperson prospects ({verified.name})\n\n{verified.read_text()}")

    candidates = latest_file(PROSPECTS, "*-candidates.csv")
    if candidates:
        parts.append(f"# Candidate prospects (need verification)\n\n{candidates.read_text()}")

    intel = latest_file(INTEL, "*-intel.json")
    if intel:
        parts.append(f"# Raw intel from research agents\n\n{intel.read_text()}")

    return "\n\n---\n\n".join(parts) if parts else "No briefs yet — run `python -m scout.orchestrator` first."


SYSTEM_PROMPT = """You are Blake's content + sales strategist for Ventrix — a B2B SaaS Chrome extension that auto-fills Facebook Marketplace listings for car dealerships in 10-15 seconds per car (vs 20-25 minutes manually).

Your context: the user is Blake (Ventrix's marketing partner). You have access to this week's content brief, the verified salesperson prospect list, raw intel from research agents, and the live web (via web_search).

Your job: answer Blake's questions tactically. He's busy and posting daily — give him short, specific, action-ready answers.

What Blake will ask about:
- Which post format to use today
- Which prospects to DM first and what to say
- Whether a hook idea will land
- How to react to something a competitor just did
- Should he reply to a specific comment / DM thread

Voice you respond in: cocky, specific, no fluff. Match Ventrix's brand voice. Never reveal pricing in any caption or DM you draft.

Ventrix value props (only claim what's true today):
- Auto-fills FB Marketplace listing in 10-15 sec/car (vs 20-25 min manual)
- AI descriptions in dealer's voice
- Auto-takedown when sold in DMS
- Manager dashboard + posted-by-name tracking
- Lead Engine v1: phone pings 5/30/60 min when buyer messages
- Concierge white-glove setup

DON'T claim: auto-calling, auto-texting, auto-test-drive booking, drip sequences.

NEVER include dollar amounts in any caption/DM/post you draft for Blake. CTAs are: 'DM us', 'free trial', 'ventrix.tech', 'book a call'.

If Blake asks something current-events that needs fresh info, use the `web_search` tool."""


def chat():
    client = Anthropic()
    context = load_context()
    history: list[dict] = []

    print("🧠 Ventrix scout chat — talk to your content + sales strategist")
    print("    Type 'quit' or Ctrl-D to exit. Type 'reload' to refresh context.\n")

    while True:
        try:
            user_input = input("Blake > ").strip()
        except EOFError:
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if user_input.lower() == "reload":
            context = load_context()
            print("  (context reloaded)\n")
            continue

        # Build messages with context only on the FIRST turn
        if not history:
            framed_input = (
                f"CONTEXT FROM THIS WEEK'S SCOUT RUN:\n\n{context}\n\n"
                f"---\n\nBlake's question: {user_input}"
            )
        else:
            framed_input = user_input
        history.append({"role": "user", "content": framed_input})

        try:
            msg = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 4,
                }],
                messages=history,
            )
            assistant_text = "\n".join(
                b.text for b in msg.content if getattr(b, "type", None) == "text"
            ).strip()
            history.append({"role": "assistant", "content": msg.content})
            print(f"\nScout > {assistant_text}\n")
        except Exception as e:
            print(f"  ⚠️ error: {e}\n")
            history.pop()  # drop the user turn that failed


if __name__ == "__main__":
    chat()

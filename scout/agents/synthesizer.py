"""Synthesizer — takes outputs from all research agents and produces the weekly Ventrix content brief."""
import json
from typing import Any, Dict, List

from ..lib.claude import SMART_MODEL, run_agent


SYSTEM = """You are the head of content for Ventrix — a B2B SaaS Chrome extension that auto-fills Facebook Marketplace listings for car dealerships in 10-15 seconds per car (vs 20-25 minutes manually).

Ventrix sells to TWO audiences on Instagram + TikTok + X:

AUDIENCE A — Dealers (Used Car Managers, GMs, Internet Sales Managers, BDC Managers, Dealer Principals)
• They care about: ROI, team productivity, fewer hours wasted by their staff, manager dashboard, beating the dealership down the street.
• Voice angle: "we make your TEAM faster."

AUDIENCE B — Individual car salespeople
• They care about: personal commission, beating coworkers, more posts → more buyer DMs → more deals on THEIR name.
• Voice angle: "we make YOU the top closer."

Ventrix value props (only claim what is true today):
- Auto-fills FB Marketplace listing form in 10-15 sec per car
- AI descriptions in dealer's voice
- Auto-takedown when car is marked sold in DMS
- Manager dashboard with posted-by-name tracking
- Lead Engine v1: phone pings in 5 / 30 / 60 min when buyer messages on Marketplace
- Concierge white-glove setup (founder handles days 1-5)

DO NOT claim (roadmap, not today):
- Auto-calling leads, auto-texting leads, auto-booking test drives, drip sequences.

Brand voice: punchy, cocky, specific. Specific numbers > vague claims. Cocky, not corporate. No emojis in headlines.

PUBLIC CONTENT RULE: NEVER include pricing ($1,500, $499, $300, $100, any monthly amount) in any post. CTAs are "DM us", "book a free trial", "schedule a call", "ventrix.tech".

Banned phrases: "innovative SaaS solution", "streamline your workflow", "supercharge", "revolutionize", "10x your X", "synergy", "leverage", "game-changer", "next-gen", "AI-powered"."""


def build_user_prompt(
    week_label: str,
    x_signals: List[Dict[str, Any]],
    reddit_signals: List[Dict[str, Any]],
    meme_signals: List[Dict[str, Any]],
    competitor_signals: List[Dict[str, Any]],
) -> str:
    return f"""I've collected this week's social intel for Ventrix. Use it to produce the next weekly content brief — 21 posts total (3/day x 7 days, Monday through Sunday).

WEEK LABEL: {week_label}

X/TWITTER VIRAL B2B SaaS POSTS (last 7 days):
{json.dumps(x_signals, indent=2)}

REDDIT FOUNDER STORIES (last 7 days):
{json.dumps(reddit_signals, indent=2)}

TRENDING MEME FORMATS (current):
{json.dumps(meme_signals, indent=2)}

COMPETITOR SIGNALS (last 7-14 days):
{json.dumps(competitor_signals, indent=2)}

PRODUCE THE BRIEF as a single markdown document with these sections:

# Ventrix Content Brief — Week of {week_label}

## ⚡ This week's TL;DR for Blake
3-5 sentences. The single biggest pattern you noticed this week, the format Blake should hit hardest, and which 2-3 trending signals to ride first.

## 🎯 Banned phrases
List the banned phrases.

## 📡 This week's top signals to study
Paste 5-8 of the strongest specific URLs from the intel above with a one-line "why this hits" annotation.

## 🥊 Competitor watch
Summarize 2-3 competitor moves from the intel + the counter-angle Ventrix can take.

## 📅 21 posts — 3 per day, Mon → Sun
For each day, three posts. For each post, include:
- **Audience:** [DEALER] / [SALESPERSON] / [BOTH]
- **Platform:** (X / IG / TikTok / LinkedIn)
- **Format:** (the trending format from the intel it borrows from)
- **Hook to use** (the actual first line — 1-2 lines max)
- **Body / structure** (2-4 lines, what comes after the hook)
- **CTA** (which non-pricing CTA closes it)
- **🔥 Riding off:** (one trending signal URL with one-sentence reason)

Mix the audience tags so dealer/salesperson/both are balanced across the week (~50% salesperson, ~30% dealer, ~20% both — salespeople convert faster).

Variety mandate: don't repeat the same format twice in a row. Rotate at least 6 different formats across the 21 posts.

Output ONLY the markdown brief. No preamble, no commentary outside the markdown."""


def run(
    week_label: str,
    x_signals: List[Dict[str, Any]],
    reddit_signals: List[Dict[str, Any]],
    meme_signals: List[Dict[str, Any]],
    competitor_signals: List[Dict[str, Any]],
) -> str:
    user = build_user_prompt(
        week_label, x_signals, reddit_signals, meme_signals, competitor_signals
    )
    return run_agent(
        system=SYSTEM,
        user=user,
        model=SMART_MODEL,
        enable_web_search=False,
        max_tokens=8000,
    )

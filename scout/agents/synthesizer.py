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
    days: int = 7,
    day_labels: List[str] | None = None,
) -> str:
    total_posts = days * 3
    days_list = "\n".join(f"- {d}" for d in (day_labels or []))
    return f"""I've collected this week's social intel for Ventrix. Use it to produce the next content brief — {total_posts} posts total (3/day x {days} days).

START DATE: {week_label}
DAYS COVERED: {days}
EXACT DAY LABELS TO USE (in order):
{days_list}

X/TWITTER VIRAL B2B SaaS POSTS (last 7 days):
{json.dumps(x_signals, indent=2)}

REDDIT FOUNDER STORIES (last 7 days):
{json.dumps(reddit_signals, indent=2)}

TRENDING MEME FORMATS (current):
{json.dumps(meme_signals, indent=2)}

COMPETITOR SIGNALS (last 7-14 days):
{json.dumps(competitor_signals, indent=2)}

PRODUCE THE BRIEF as a single markdown document with these sections:

# Ventrix Content Brief — Starting {week_label}

## ⚡ TL;DR for Blake
3-5 sentences. The single biggest pattern you noticed this week, the format Blake should hit hardest, and which 2-3 trending signals to ride first.

## 🎯 Banned phrases
List the banned phrases.

## 📡 Top signals to study
Paste 5-8 of the strongest specific URLs from the intel above with a one-line "why this hits" annotation.

## 🥊 Competitor watch
Summarize 2-3 competitor moves from the intel + the counter-angle Ventrix can take.

## 📅 {total_posts} posts — 3 per day for {days} day(s)

⚠️ HARD RULE: every post MUST be a direct recreation of a real trending post from the intel sections above. No invented hooks. No "ideas." Pick a specific URL, quote its actual hook, then write the Ventrix version that maps it 1:1.

If you do not have a real specific trending URL with a real hook from the intel for a given slot, say so explicitly in that slot (e.g. "⚠️ no live signal matched this slot — Blake, post format X using your own copy") rather than inventing one.

Use the EXACT day labels listed above, in order. For each day, three posts. For each post use THIS exact structure:

- **Audience:** [SALESPERSON] / [OWNER] / [BOTH]
- **Platform:** (X / IG / TikTok / LinkedIn)
- **🎯 The trending post we're stealing from:**
  - URL: <the exact URL from the intel sections>
  - Creator: <handle>
  - Engagement: <view/like count from the intel>
  - Their actual hook (quoted verbatim from the intel): "<their exact opening line>"
  - Why it worked: <one sentence from the intel>
- **🔁 Ventrix version of that post:**
  - **Hook (paste-ready):** <one-line Ventrix opener that mirrors the trending hook's structure word-for-word>
  - **Body / structure (paste-ready):** <2-4 lines following the same beat as the original>
  - **CTA:** <non-pricing CTA>

Audience mix target: ~70% SALESPERSON (Blake's primary funnel), ~20% OWNER, ~10% BOTH.

POSITIONING ORDER (every post): time savings is the headline (22 min vs 10-15 sec per car). Features are second. Ban safety is ONLY for posts comparing to CARVID/Shiftly/AutoXcel — never lead with it.

Variety mandate: every post must reference a DIFFERENT trending URL. If the intel only contains N unique URLs and you need more posts than N, repeat the highest-engagement ones first.

Output ONLY the markdown brief. No preamble."""


def run(
    week_label: str,
    x_signals: List[Dict[str, Any]],
    reddit_signals: List[Dict[str, Any]],
    meme_signals: List[Dict[str, Any]],
    competitor_signals: List[Dict[str, Any]],
    days: int = 7,
    day_labels: List[str] | None = None,
) -> str:
    user = build_user_prompt(
        week_label, x_signals, reddit_signals, meme_signals,
        competitor_signals, days=days, day_labels=day_labels,
    )
    return run_agent(
        system=SYSTEM,
        user=user,
        model=SMART_MODEL,
        enable_web_search=False,
        max_tokens=8000,
    )

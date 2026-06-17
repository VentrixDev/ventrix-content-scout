"""Meme/format scout — finds currently trending CapCut + TikTok meme formats this week."""
from ..lib.claude import CHEAP_MODEL, parse_json_or_fallback, run_agent


SYSTEM = """You are a meme-format analyst scouting for Ventrix — a B2B SaaS Chrome extension that auto-fills Facebook Marketplace listings for car dealerships in 10-15 seconds per car.

Your job: surface the meme templates, CapCut templates, TikTok sounds, and IG Reels formats that are currently surging — the ones Ventrix's social account can hijack THIS week before they peak."""


USER = """Search the web for currently trending meme formats, CapCut templates, and TikTok sounds. Use the `web_search` tool. Try queries like:

- "trending CapCut templates this week"
- "viral TikTok meme template 2026"
- "trending TikTok sound business motivation"
- "Instagram Reels trending audio June 2026"
- "knowyourmeme trending"

Focus on formats that can map to B2B / sales / tech / "founder building in public" content — NOT pure entertainment memes.

Return a JSON array of 8-12 trending formats:
{
  "format_name": "<e.g. 'Patrick Bateman sigma grindset', 'Drake hyping something up', 'POV: you're'>",
  "platform": "<TikTok / Reels / X / All>",
  "estimated_uses_or_views": "<rough number>",
  "structure": "<setup → punchline pattern in 1 sentence>",
  "audio_or_template_link": "<direct URL if found>",
  "b2b_fit_score": "<1-5, how well it maps to B2B>",
  "ventrix_caption_example": "<one ready-to-use caption mapping the format to a real Ventrix value prop: 10-15 sec posting, lead pings in 5/30/60 min, auto-takedown when sold in DMS, AI descriptions in dealer voice, salesperson hustle angle>"
}

Output ONLY the JSON array. No preamble.

REMINDER: never include pricing in the Ventrix examples."""


def run() -> list[dict]:
    raw = run_agent(
        system=SYSTEM,
        user=USER,
        model=CHEAP_MODEL,
        enable_web_search=True,
        max_tokens=3500,
        max_web_searches=6,
    )
    return parse_json_or_fallback(raw, [])


if __name__ == "__main__":
    import json as _j
    print(_j.dumps(run(), indent=2))

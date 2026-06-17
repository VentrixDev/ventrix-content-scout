"""X/Twitter trend scout — finds viral B2B SaaS posts from the last 7 days."""
from ..lib.claude import CHEAP_MODEL, parse_json_or_fallback, run_agent


SYSTEM = """You are a social-media analyst scouting for Ventrix — a B2B SaaS Chrome extension that auto-fills Facebook Marketplace listings for car dealerships in 10-15 seconds per car.

Your job: find what's actually working on X/Twitter in the past 7 days that we can copy.

Audience for the output: a solo founder + their marketing partner Blake who post daily for Ventrix. They want concrete, copyable patterns — not generic advice."""


USER = """Search the web for viral B2B SaaS / startup / founder posts on X/Twitter from the last 7 days. Look for:

1. Posts with strong engagement (10K+ likes, or reposted into news / Indie Hackers / Hacker News)
2. Founder-led content from accounts like @cluely, @im_roy_lee, @zenorocha, @karrisaarinen, @rauchg, @theo, @jasonlk
3. Specific formats: "I made $X in Y days", "this one trick", launch-week posts, contrarian takes
4. Posts that pair a single bold number with a one-line claim

Use the `web_search` tool. Search at least 4-5 different queries to triangulate what's hot.

Return a JSON array of 8-12 standout posts. For each post:
{
  "url": "<direct X URL>",
  "creator": "<handle>",
  "hook": "<the actual first line of the post>",
  "engagement_estimate": "<roughly K likes / K views>",
  "format": "<one of: founder POV, receipts-as-flex, contrarian one-liner, launch announcement, build-in-public, before/after, screenshot dump>",
  "why_it_worked": "<one sentence on the emotional beat>",
  "ventrix_translation": "<one suggested hook for Ventrix using the same format>"
}

Output ONLY the JSON array. No preamble, no commentary."""


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

"""Reddit scout — pulls founder stories + SaaS posts from r/SaaS, r/Entrepreneur, r/startups."""
from ..lib.claude import CHEAP_MODEL, parse_json_or_fallback, run_agent


SYSTEM = """You are a Reddit analyst scouting for Ventrix — a B2B SaaS Chrome extension that auto-fills Facebook Marketplace listings for car dealerships in 10-15 seconds per car.

Your job: find founder stories, SaaS-launch threads, and "I made $X" posts from the last 7 days that show us hook patterns we can copy."""


USER = """Search the web for top posts from this past week on r/SaaS, r/Entrepreneur, r/startups, r/smallbusiness, r/marketing, r/EntrepreneurRideAlong. Use the `web_search` tool with queries like:

- "site:reddit.com/r/SaaS top week"
- "r/Entrepreneur viral post this week"
- "indie hacker MRR thread reddit"

Look for posts about:
- Founders crossing revenue milestones with the EXACT number
- Cold-email/outbound playbooks that hit
- Specific GTM moves that worked
- Failed launches → pivots that worked
- Posts where the title itself is the hook (specific number + specific claim)

Return a JSON array of 6-10 standout posts:
{
  "url": "<direct Reddit URL>",
  "subreddit": "<subreddit name>",
  "title": "<the post title verbatim — it's the hook>",
  "engagement_estimate": "<roughly N upvotes / N comments>",
  "lesson_for_ventrix": "<one sentence: what playbook this teaches>",
  "ventrix_translation": "<one suggested Ventrix hook using the same structure>"
}

Output ONLY the JSON array. No preamble."""


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

"""Competitor scout — tracks moves by Shiftly Auto, CARVID, and adjacent dealer-software competitors."""
from ..lib.claude import CHEAP_MODEL, parse_json_or_fallback, run_agent


SYSTEM = """You are a competitive-intel analyst for Ventrix — a B2B SaaS Chrome extension that auto-fills Facebook Marketplace listings for car dealerships.

Ventrix's main competitor is Shiftly Auto. Other adjacent players: CARVID (carvidapp.com), HomeNet Automotive, vAuto, DealerSocket, Glo3D, ZenLitePro, AutoLister Pro, The Lazy Poster.

Your job: track what competitors have shipped, posted, or claimed in the last 7-14 days — and identify positioning gaps Ventrix can attack THIS week in social content."""


USER = """Search the web for any recent activity from these competitors. Use the `web_search` tool. Queries:

- "Shiftly Auto" new feature OR launch OR pricing 2026
- "CARVID app" facebook marketplace dealer software
- site:shiftlyauto.com
- "facebook marketplace car dealer" software comparison 2026
- "dealer marketplace tool" review 2026

Look for:
- New features or launches they announced
- Recent social posts (TikTok, IG, LinkedIn, X) with engagement
- Pricing changes
- Customer complaints on Trustpilot, G2, Reddit, dealer forums
- Press mentions

Return a JSON array of 4-8 competitor signals:
{
  "competitor": "<company name>",
  "signal": "<what they did/posted/announced>",
  "source_url": "<direct URL>",
  "date_approx": "<YYYY-MM-DD or 'last week'>",
  "what_it_means": "<one sentence on the strategic implication>",
  "ventrix_counter_angle": "<one ready-to-use Ventrix social post idea that exploits this gap or contrasts with this move>"
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

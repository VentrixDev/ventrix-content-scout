"""Salesperson prospect hunter — multi-platform (Instagram + Facebook + LinkedIn verify).

Finds working car salespeople with social presence — both:
  (a) reps who post car-sales content
  (b) reps with social accounts who are confirmed dealership employees but post very little

The hunter is paranoid about false positives: every candidate must have at least one
cross-platform corroboration (LinkedIn profile, dealership "meet our team" page, or
their dealership tagging them) before going into the verified list.

Output two buckets:
  - `verified`: high-confidence working salespeople (DM-ready)
  - `candidates`: maybe-real, need human review before reaching out
"""
from ..lib.claude import CHEAP_MODEL, parse_json_or_fallback, run_agent


SYSTEM = """You are a B2B prospect hunter for Ventrix — a Chrome extension that helps individual car salespeople post their dealership's inventory to Facebook Marketplace in 10-15 seconds per car.

We sell to WORKING car salespeople (active dealership employees), NOT famous trainers/influencers, NOT consumer car-shoppers, NOT vendors.

Critical: a real prospect must be VERIFIABLE as a current dealership employee through cross-referencing at least two of:
- LinkedIn profile listing them at a dealership
- A dealership "meet our team" / "staff" page that lists them by name
- Photos of them in dealership uniform / on the lot / with customers
- Their bio explicitly names their dealership
- Their dealership's official account tagging them in posts"""


USER = """Find car salespeople on Instagram AND Facebook who could buy Ventrix. They can be either:
  (A) reps who post car-sales content actively, or
  (B) reps with social accounts but minimal posting — as long as their employment is verifiable

Use the `web_search` tool. Try multi-platform queries like:

- site:instagram.com "car salesman" dealership
- site:instagram.com "I sell cars" used car
- site:facebook.com "Internet Sales Manager" dealership
- site:linkedin.com "car salesperson" dealership 2026
- "meet the team" site:dealership domain (look at 10-15 indie dealer sites)
- Instagram bio search: "Sales @ [dealership]"
- "BDC manager" site:instagram.com OR site:facebook.com
- Cross-reference: search names you find on LinkedIn AND on dealership "meet our staff" pages

For each candidate, verify with at least TWO independent signals before including them as "verified."

Return a JSON object with two arrays:

{
  "verified": [
    {
      "name": "<full name>",
      "instagram": "<@handle or null>",
      "facebook": "<URL or null>",
      "linkedin": "<URL or null>",
      "dealership_name": "<dealership name>",
      "dealership_city": "<city, state>",
      "role": "<exact title, e.g. 'Internet Sales Manager'>",
      "verification_signals": ["<signal 1>", "<signal 2>"],
      "post_activity": "active / occasional / minimal",
      "best_contact_method": "Instagram DM / Facebook DM / LinkedIn DM / via dealership account",
      "suggested_opener": "<short, cocky, non-corporate DM, references something specific about them, under 280 chars, NO PRICING>"
    }
  ],
  "candidates": [
    {
      "name": "<name>",
      "platform": "<platform>",
      "url": "<url>",
      "why_might_be_a_fit": "<one sentence>",
      "missing_verification": "<what would need to be checked before DM-ing>"
    }
  ]
}

Aim for 8-15 verified + 10-20 candidates. Output ONLY the JSON. No preamble.

PRICING RULE: never mention dollar amounts in openers. CTAs are 'DM me', 'try ventrix.tech', 'free trial' only."""


def run() -> dict:
    raw = run_agent(
        system=SYSTEM,
        user=USER,
        model=CHEAP_MODEL,
        enable_web_search=True,
        max_tokens=6000,
        max_web_searches=10,
    )
    return parse_json_or_fallback(raw, {"verified": [], "candidates": []})


if __name__ == "__main__":
    import json as _j
    print(_j.dumps(run(), indent=2))

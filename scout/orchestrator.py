"""Ventrix multi-agent content scout.

Runs four research agents in parallel, hands the findings to a synthesizer that
produces the weekly content brief. Also runs the TikTok prospect hunter, which
outputs a CSV of car salespeople to DM.

Usage:
    python -m scout.orchestrator
"""
import csv
import datetime
import json
import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Make scout/ importable as a package whether run via `-m` or directly.
sys.path.insert(0, str(Path(__file__).parent.parent))

from scout.agents import (  # noqa: E402
    competitor_scout,
    meme_scout,
    prospect_hunter,
    reddit_scout,
    x_scout,
    synthesizer,
)


ROOT = Path(__file__).parent.parent
BRIEFS = ROOT / "briefs"
PROSPECTS = BRIEFS / "prospects"
INTEL = BRIEFS / "intel"
BRIEFS.mkdir(exist_ok=True)
PROSPECTS.mkdir(exist_ok=True)
INTEL.mkdir(exist_ok=True)


def next_monday(today: datetime.date | None = None) -> datetime.date:
    if today is None:
        today = datetime.date.today()
    # If today IS Monday, treat the brief as covering this Monday onward
    offset = (7 - today.weekday()) % 7
    if offset == 0:
        offset = 7
    return today + datetime.timedelta(days=offset)


def brief_start_date() -> datetime.date:
    """Decide what date the brief covers.

    Default: next Monday (normal Sunday cron behavior).
    Override: set BRIEF_START_DATE=YYYY-MM-DD to anchor to a specific date.
    """
    override = os.environ.get("BRIEF_START_DATE")
    if override:
        return datetime.date.fromisoformat(override)
    return next_monday()


def brief_days() -> int:
    """How many days the brief covers. Default 7 (a week). Override BRIEF_DAYS=N."""
    return int(os.environ.get("BRIEF_DAYS", "7"))


def run_research_agents() -> dict:
    """Run research agents sequentially with delays to respect Anthropic rate limits.

    The default API tier caps input at 50K tokens/min — running 4 web-search agents
    in parallel will burst over that. Sequential with a short cool-down between
    agents stays well under the limit and adds only ~2 min to total runtime.
    """
    import time
    agents = [
        ("x_signals", x_scout.run),
        ("reddit_signals", reddit_scout.run),
        ("meme_signals", meme_scout.run),
        ("competitor_signals", competitor_scout.run),
    ]
    results: dict = {}
    for i, (name, fn) in enumerate(agents):
        try:
            results[name] = fn()
            print(f"  ✅ {name}: {len(results[name])} items")
        except Exception as e:
            print(f"  ⚠️ {name} failed: {e}")
            traceback.print_exc()
            results[name] = []
        if i < len(agents) - 1:
            time.sleep(40)  # cool-down to stay under 50K tokens/min on default tier
    return results


def write_prospects_csvs(prospects: dict, week_label: str) -> tuple[Path, Path]:
    """Write two CSVs: verified (DM-ready) and candidates (need human review)."""
    verified_out = PROSPECTS / f"week-of-{week_label}-verified.csv"
    candidates_out = PROSPECTS / f"week-of-{week_label}-candidates.csv"

    verified_fields = [
        "name", "instagram", "facebook", "linkedin", "dealership_name",
        "dealership_city", "role", "verification_signals", "post_activity",
        "best_contact_method", "suggested_opener",
    ]
    candidates_fields = [
        "name", "platform", "url", "why_might_be_a_fit", "missing_verification",
    ]

    def write_csv(path, fields, rows):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                # Flatten lists for CSV
                row = {}
                for k in fields:
                    v = r.get(k, "")
                    row[k] = " · ".join(v) if isinstance(v, list) else v
                w.writerow(row)

    write_csv(verified_out, verified_fields, prospects.get("verified", []))
    write_csv(candidates_out, candidates_fields, prospects.get("candidates", []))
    return verified_out, candidates_out


def write_intel(week_label: str, intel: dict) -> Path:
    out = INTEL / f"week-of-{week_label}-intel.json"
    out.write_text(json.dumps(intel, indent=2))
    return out


def main() -> None:
    start = brief_start_date()
    days = brief_days()
    week_label = start.strftime("%Y-%m-%d")
    print(f"🚀 Ventrix multi-agent scout — brief starting {week_label} for {days} day(s)\n")

    print("📡 Running research agents in parallel…")
    intel = run_research_agents()

    print("\n🎯 Running multi-platform salesperson hunter (IG + FB + LinkedIn verify)…")
    import time as _t
    _t.sleep(40)  # cool-down before the next big run
    prospects = {"verified": [], "candidates": []}
    try:
        prospects = prospect_hunter.run()
        print(f"  ✅ {len(prospects.get('verified', []))} verified + {len(prospects.get('candidates', []))} candidates")
    except Exception as e:
        print(f"  ⚠️ prospect hunter failed: {e}")
        traceback.print_exc()

    print("\n🧠 Synthesizing brief…")
    day_labels = [
        (start + datetime.timedelta(days=i)).strftime("%A %b %d")
        for i in range(days)
    ]
    try:
        brief = synthesizer.run(
            week_label=week_label,
            x_signals=intel.get("x_signals", []),
            reddit_signals=intel.get("reddit_signals", []),
            meme_signals=intel.get("meme_signals", []),
            competitor_signals=intel.get("competitor_signals", []),
            days=days,
            day_labels=day_labels,
        )
    except Exception as e:
        print(f"  ⚠️ synthesizer failed: {e}")
        traceback.print_exc()
        brief = (
            f"# Ventrix Content Brief — Starting {week_label}\n\n"
            "*Synthesizer failed this run. See `briefs/intel/` for raw agent outputs.*\n"
        )

    brief_path = BRIEFS / f"week-of-{week_label}.md"
    brief_path.write_text(brief)
    verified_path, candidates_path = write_prospects_csvs(prospects, week_label)
    intel_path = write_intel(week_label, intel)

    print(f"\n✅ Brief:           {brief_path}")
    print(f"✅ Verified leads:  {verified_path}")
    print(f"✅ Candidates:      {candidates_path}")
    print(f"✅ Raw intel:       {intel_path}")


if __name__ == "__main__":
    main()

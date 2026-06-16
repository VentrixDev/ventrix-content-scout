"""Ventrix Content Scout — runs weekly, produces a 7-day posting brief.

Pulls from free sources only (no paid APIs):
  - Reddit JSON endpoints (r/SaaS, r/startups, r/marketing, r/Entrepreneur)
  - Public RSS feeds (Indie Hackers, HN front page)
  - KnowYourMeme trending RSS

Synthesizes a weekly brief using a deterministic template engine (no LLM cost).
Output: briefs/week-of-YYYY-MM-DD.md with 21 post ideas (3/day x 7 days).
"""

import datetime
import json
import os
import random
import re
import urllib.request
import urllib.parse
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parent
DATA = ROOT / "data"
BRIEFS = ROOT / "briefs"
BRIEFS.mkdir(exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ---------- Source fetchers (free, no auth) ----------


def fetch_url(url, timeout=15):
    """Plain GET with a real user agent. Returns bytes or None."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        print(f"  ⚠️ fetch failed {url}: {e}")
        return None


def reddit_top(subreddit, t="week", limit=10):
    """Reddit RSS feed (works without auth; the JSON endpoint started blocking generic UAs)."""
    url = f"https://www.reddit.com/r/{subreddit}/top/.rss?t={t}&limit={limit}"
    raw = fetch_url(url)
    if not raw:
        return []
    text = raw.decode("utf-8", errors="ignore")
    out = []
    # Crude but reliable XML parsing
    entries = re.findall(
        r"<entry>(.*?)</entry>", text, re.DOTALL
    )
    for entry in entries:
        title_m = re.search(r"<title[^>]*>(.*?)</title>", entry, re.DOTALL)
        link_m = re.search(r'<link[^>]+href="([^"]+)"', entry)
        if not (title_m and link_m):
            continue
        title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()
        out.append({
            "title": title,
            "url": link_m.group(1),
            "score": 0,  # RSS doesn't expose score; we keep it for shape compatibility
            "comments": 0,
            "subreddit": subreddit,
        })
    return out[:limit]


def hackernews_top(limit=15):
    """HN front page via Firebase API."""
    ids_raw = fetch_url("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not ids_raw:
        return []
    try:
        ids = json.loads(ids_raw.decode("utf-8"))[:limit]
    except Exception:
        return []
    out = []
    for sid in ids:
        item_raw = fetch_url(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        if not item_raw:
            continue
        try:
            item = json.loads(item_raw.decode("utf-8"))
            if not item:
                continue
            out.append({
                "title": item.get("title", "").strip(),
                "url": item.get("url") or f"https://news.ycombinator.com/item?id={sid}",
                "score": item.get("score", 0),
                "comments": item.get("descendants", 0),
                "source": "hn",
            })
        except Exception:
            continue
    return out


# ---------- Filters: keep only "tech that sells Ventrix" content ----------

KEEP_KEYWORDS = [
    "saas", "startup", "founder", "marketing", "growth", "viral",
    "cold email", "outbound", "sales", "b2b", "automation", "chrome extension",
    "marketplace", "facebook", "instagram", "tiktok", "social media",
    "content", "thread", "twitter", "x.com", "build in public",
    "indie hacker", "ai tool", "no-code", "launch", "revenue", "pricing",
    "customer", "user", "product", "design", "brand", "logo", "demo",
    "feature", "ship", "released", "built", "scaling", "scale", "growth",
    "acquisition", "retention", "churn", "mrr", "arr", "icp",
    "ad", "ads", "facebook ads", "tiktok ads", "instagram ads",
    "dealer", "car", "vehicle", "auto",
]

DROP_KEYWORDS = [
    "elon", "trump", "biden", "politics", "religion",
    "cryptocurrency", "crypto", "bitcoin", "nft",
    "ukraine", "russia", "israel", "gaza",
    "anime", "kpop", "music",
    "car repair", "diy", "subreddit drama",
]


def is_relevant(post):
    """Keep only B2B / SaaS / sales / content-marketing posts."""
    t = (post.get("title") or "").lower()
    if not t:
        return False
    if any(d in t for d in DROP_KEYWORDS):
        return False
    if any(k in t for k in KEEP_KEYWORDS):
        return True
    return False


# ---------- Brief generation ----------


def load_value_props():
    with open(DATA / "ventrix_value_props.json") as f:
        return json.load(f)


def pick_post_for_slot(value_props, formats, used_formats, slot_index, audience_pref):
    """Pick a (value_prop, format) pairing for a given day/slot.

    Rotates through value props and formats so the week has variety.
    audience_pref: 'dealer', 'salesperson', or 'both' — biases the rotation.
    """
    candidates = [v for v in value_props
                  if v["audience"] == audience_pref or v["audience"] == "both"]
    vp = candidates[slot_index % len(candidates)]
    # pick a format we haven't used today; reset weekly
    format_pool = [f for f in formats if f["name"] not in used_formats]
    if not format_pool:
        format_pool = formats[:]
        used_formats.clear()
    fmt = format_pool[slot_index % len(format_pool)]
    used_formats.add(fmt["name"])
    return vp, fmt


def build_post_idea(day_label, slot, value_prop, fmt, hook, signals):
    """Render one post idea as a markdown block."""
    inspiration = ""
    if signals:
        sig = signals[(hash(day_label + str(slot)) % len(signals))]
        inspiration = f"\n**🔥 Riding off this week's signal:** [{sig['title'][:80]}]({sig['url']})"

    return f"""### {day_label} · Post {slot}: {fmt['name']}

**Platform:** {fmt['platform']}
**Audience:** {value_prop['audience']}
**Value prop:** {value_prop['claim']}

**Hook to use:**
> {hook}

**Format structure:**
{fmt['structure']}

**Example to copy:** {fmt['example']}{inspiration}

---
"""


def build_weekly_brief(today=None):
    """Produce the full weekly brief markdown."""
    if today is None:
        today = datetime.date.today()
    # Anchor to Monday (start of posting week)
    start = today + datetime.timedelta(days=(0 - today.weekday()) % 7)
    config = load_value_props()
    value_props = config["value_props"]
    formats = config["post_formats"]

    # Pull live signals (best-effort; brief still works if all fail)
    print("📡 Fetching signals from Reddit + HN…")
    signals = []
    import time
    for sub in ["SaaS", "startups", "marketing", "Entrepreneur", "smallbusiness"]:
        signals.extend(reddit_top(sub, t="week", limit=8))
        time.sleep(2)  # avoid Reddit 429 rate-limit on RSS endpoint
    signals.extend(hackernews_top(limit=20))
    relevant = [s for s in signals if is_relevant(s)]
    relevant.sort(key=lambda s: s.get("score", 0), reverse=True)
    top_signals = relevant[:15]
    print(f"  ✅ Kept {len(top_signals)} relevant signals out of {len(signals)} pulled")

    # Build 7 days × 3 posts
    days = []
    audience_rotation = ["dealer", "salesperson", "both"]
    used_formats = set()
    for d in range(7):
        date = start + datetime.timedelta(days=d)
        day_label = date.strftime("%A %b %d")
        posts = []
        for slot in range(1, 4):
            audience_pref = audience_rotation[(d + slot) % 3]
            vp, fmt = pick_post_for_slot(
                value_props, formats, used_formats,
                slot_index=d * 3 + slot,
                audience_pref=audience_pref,
            )
            hook = vp["hooks"][slot % len(vp["hooks"])]
            posts.append(build_post_idea(day_label, slot, vp, fmt, hook, top_signals))
        days.append((day_label, posts))

    # Render brief
    week_label = start.strftime("%Y-%m-%d")
    out = [f"# Ventrix Content Brief — Week of {week_label}\n"]
    out.append(f"*Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}*\n")
    out.append("**21 posts (3/day × 7 days). Blake: post 1 per slot, swap in your photos/screenshots.**\n")
    out.append("---\n")
    out.append("## 🎯 This week's banned phrases\n")
    out.append("Don't use any of these — they read as corporate AI slop:\n")
    for ph in config["banned_phrases"]:
        out.append(f"- ~~{ph}~~")
    out.append("")
    out.append("## 📡 Top trending signals from this week\n")
    out.append("Read these before posting. The patterns that won here are what's working *right now* in your space.\n")
    if top_signals:
        for s in top_signals[:10]:
            out.append(f"- [{s['title'][:120]}]({s['url']}) — score {s.get('score', 0)}")
    else:
        out.append("*(no signals fetched — running offline. Brief still valid; just no fresh trends.)*")
    out.append("\n---\n")
    out.append("## 📅 Daily posts\n")
    for day_label, posts in days:
        out.append(f"## {day_label}\n")
        for p in posts:
            out.append(p)
    return "\n".join(out), week_label


def main():
    print("🚀 Ventrix Content Scout — building weekly brief")
    brief_md, week_label = build_weekly_brief()
    out_path = BRIEFS / f"week-of-{week_label}.md"
    out_path.write_text(brief_md)
    print(f"\n✅ Brief written to {out_path}")
    print(f"   Size: {len(brief_md):,} chars")
    print(f"   Open it: open '{out_path}'")


if __name__ == "__main__":
    main()

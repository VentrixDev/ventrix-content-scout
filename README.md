# Ventrix Content Scout

Automated weekly content brief for Ventrix's social media (IG, X, TikTok, LinkedIn).

**Output:** every Sunday night, a fresh `briefs/week-of-YYYY-MM-DD.md` with 21 posts ready (3/day × 7 days), mapped to Ventrix's value props and audiences (dealers + individual salespeople).

## How it works

1. **GitHub Action fires every Sunday at 2pm EST** (`.github/workflows/weekly.yml`)
2. `scout/scout.py` runs:
   - Pulls trending posts from Reddit (r/SaaS, r/startups, r/marketing, r/Entrepreneur, r/smallbusiness) via free JSON API
   - Pulls Hacker News front page via Firebase API
   - Filters to B2B-SaaS-relevant signals only
   - Generates 21 posts using the rotation engine in `data/ventrix_value_props.json`
3. **Auto-commits** the new brief to `briefs/`

## Cost: $0/month

- GitHub Actions: free (2,000 minutes/month — we use ~2 min/week)
- Reddit + HN APIs: free, no auth
- No LLM API calls — uses deterministic template engine

## How Blake uses it

Every Monday morning:
1. Open the latest file in `briefs/`
2. Pick the day's 3 posts (Monday slot 1, 2, 3)
3. Each post has: format, audience, hook, structure, example
4. Open CapCut/Canva, build the post in 5-10 min, post
5. Repeat tomorrow

## Run locally

```bash
cd ventrix-content-scout
python3 scout/scout.py
```

The brief appears in `briefs/week-of-YYYY-MM-DD.md`.

## Customize what Ventrix posts

Edit `data/ventrix_value_props.json`:

- `value_props[]` — claims with rotating hooks
- `post_formats[]` — visual layouts to rotate through
- `voice_rules[]` — style rules
- `banned_phrases[]` — words the brief refuses to use

⚠️ **Public content rule:** never reveal pricing. The data file enforces this — pricing fields are intentionally removed.

## Branding

- Brand color: `#393cfb` (electric indigo) — the V mark
- Logo files: see `~/Desktop/Ventrix Branding/transparent/`
  - `ventrix-logo-dark-bg.png` — for dark slides
  - `ventrix-logo-light-bg.png` — for light slides
  - `ventrix-v-mark.png` — for tight corners

## What's in a brief

```
# Ventrix Content Brief — Week of 2026-06-16

[21 posts: 3/day × 7 days]
[Each post: format, audience, hook, structure, example]

📡 Top trending signals from the week (10 links to study)
🎯 Banned phrases (don't write these)
📅 Daily posts (Mon-Sun, 3 slots each)
```

## Deploy to GitHub

```bash
gh repo create ventrix-content-scout --private --source=. --push
# Action will run automatically every Sunday at 18:00 UTC
```

Or push manually:
```bash
git remote add origin git@github.com:YOUR-USERNAME/ventrix-content-scout.git
git branch -M main
git push -u origin main
```

## Trigger a brief manually

In GitHub: **Actions tab → Weekly Ventrix Content Brief → Run workflow**

Or locally: `python3 scout/scout.py`

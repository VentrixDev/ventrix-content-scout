# Ventrix Content Scout

Automated weekly content brief for Ventrix's social media (IG, X, TikTok, LinkedIn).

**Output:** every Sunday night, a fresh `briefs/week-of-YYYY-MM-DD.md` with 21 posts ready (3/day × 7 days), mapped to Ventrix's value props and audiences (dealers + individual salespeople).

## How it works (multi-agent v2)

1. **GitHub Action fires every Sunday at 2pm EST** (`.github/workflows/weekly.yml`)
2. `scout/orchestrator.py` runs 4 research agents + 1 prospect hunter + 1 synthesizer:
   - **x_scout** — viral B2B SaaS posts on X from last 7 days
   - **reddit_scout** — founder-story posts from r/SaaS, r/Entrepreneur, r/startups
   - **meme_scout** — currently trending CapCut templates + TikTok sounds
   - **competitor_scout** — Shiftly + CARVID + dealer SaaS competitor moves
   - **prospect_hunter** — Instagram + Facebook car salespeople, cross-verified via LinkedIn
   - **synthesizer** — Sonnet model produces the 21-post weekly brief from all intel
3. **Auto-commits** brief + prospect CSVs + raw intel to the repo

## Cost: ~$1-3/week

- GitHub Actions: free
- Anthropic API: Haiku for research passes + Sonnet for synthesis
- Web search: ~$10 per 1000 queries (we use ~30/week = ~$0.30)

## Blake's interactive chat agent

```bash
python -m scout.chat
```

Loads the latest brief + prospect list + raw intel. Blake asks questions like
"which post should I make today" or "draft a DM for prospect #3" and gets cocky,
specific answers — with web search if needed.

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

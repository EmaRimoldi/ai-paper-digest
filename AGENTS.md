# AI Paper Radar Agents Guide

## Purpose

Maintain a daily AI paper radar that fetches recent papers, ranks the strongest items, stores private reading artifacts locally, and publishes a GitHub-safe public catalog.

## Public/Private Boundary

- Never commit `library/` contents.
- Never commit `email/latest_digest.md`.
- Treat `data/*.jsonl` and `data/seen_ids.txt` as local working state.
- Only publish generated notes, SVG assets, docs, and `data/papers.csv`.
- Do not publish paper figures unless their reuse license is explicit and attribution is included.

## Core Commands

```bash
python scripts/run_daily_pipeline.py --no-push
python scripts/validate_data.py
python scripts/publish_github.py --no-push
```

## Editing Guidance

- Keep public paper notes short and evidence-bound.
- If a summary only uses metadata or an abstract, say so explicitly.
- Prefer generated original SVG cards over reused paper figures.
- Preserve stable topic slugs and avoid aggressive taxonomy churn.


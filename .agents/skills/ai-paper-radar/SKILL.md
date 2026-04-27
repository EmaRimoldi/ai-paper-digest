---
name: ai-paper-radar
description: Build a daily AI research paper radar for Emanuele by fetching, deduplicating, ranking, saving, summarizing, cataloging, and optionally publishing the top AI papers to GitHub. Use when Codex needs to run or maintain the recurring paper-digest workflow, update the public catalog, generate short paper notes, refresh visual assets, or validate that public outputs do not leak private PDFs, email data, or unsafe figures.
---

# Goal

Run a daily AI paper radar workflow for Emanuele.

# Persistent Files

Read and update:
- `config/profile.yml`
- `config/sources.yml`
- `config/social_sources.yml`
- `config/researchers.yml`
- `config/queries.yml`
- `config/taxonomy.yml`
- `config/scoring.yml`
- `config/email.yml`
- `config/github.yml`
- `config/limits.yml`
- `data/papers.jsonl`
- `data/papers.csv`
- `data/seen_ids.txt`
- `data/source_runs.jsonl`
- `data/daily_candidates.jsonl`
- `data/social_items.jsonl`
- `data/trending_items.jsonl`
- `data/taxonomy_assignments.jsonl`
- `library/pdfs/`
- `library/notes/`
- `library/abstracts/`
- `catalog/`
- `public/assets/`
- `reports/daily/`
- `reports/weekly/`
- `email/latest_digest.md`
- `README.md`

# Workflow

1. Load the profile, sources, social sources, researcher watchlist, queries, taxonomy, scoring, GitHub config, and limits.
2. Fetch new papers from arXiv and other configured sources.
3. Fetch permitted public research and social signals.
4. Enrich metadata from Semantic Scholar, OpenAlex, and OpenReview when available.
5. Deduplicate papers across source IDs and near-identical titles.
6. Rank candidates and select the top 10 most interesting items.
7. Save selected PDFs locally only.
8. Write short structured summaries and private notes.
9. Assign papers to the iterative topic catalog.
10. Generate public paper notes and topic pages.
11. Generate original SVG visual assets.
12. Update the root README and catalog mirrors.
13. Generate the daily report and the email digest.
14. Validate that public-safe outputs do not include private PDFs, email data, secrets, or unsafe figures.
15. Commit or push public-safe files only when configuration or the invoking prompt explicitly allows it.

# Commands

Prefer these entrypoints:
- `python scripts/run_daily_pipeline.py --no-push`
- `python scripts/validate_data.py`
- `python scripts/publish_github.py --no-push`

Use the single-step scripts only when you need to rerun or debug one stage.

# Rules

- Do not fabricate missing metadata.
- If a summary is abstract-only, say so explicitly.
- Do not scrape restricted or login-only sources.
- Do not automate LinkedIn or X/Twitter login flows.
- Do not publish raw PDFs by default.
- Do not publish copyrighted figures unless license or permission is explicit.
- Prefer original generated visual assets over reused paper figures.
- Do not send email unless explicitly authorized.
- Never email authors automatically.
- Keep public catalog notes short, clear, and useful.


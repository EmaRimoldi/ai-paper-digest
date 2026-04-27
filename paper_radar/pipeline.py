from __future__ import annotations

import argparse
import os
import subprocess
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

from .analysis import (
    build_author_index,
    build_venue_index,
    deduplicate_papers,
    ensure_schema,
    first_author_name,
    rank_papers,
    summarize_paper,
    update_taxonomy_assignments,
)
from .config import DATA_DIR, ROOT, load_all_configs, now_iso, today_local
from .render import build_catalog, generate_digest, generate_public_readme, generate_visual_assets, mirror_public_catalog
from .sources import (
    enrich_selected_from_arxiv,
    enrich_with_openalex,
    enrich_with_semantic_scholar,
    fetch_arxiv_candidates,
    fetch_gmail_alerts,
    fetch_openreview_candidates,
    fetch_social_items,
)
from .storage import append_jsonl, read_jsonl, touch, write_csv, write_jsonl, write_text
from .validation import validate_public_outputs


def initialize_workspace() -> None:
    files_to_touch = [
        DATA_DIR / "papers.jsonl",
        DATA_DIR / "seen_ids.txt",
        DATA_DIR / "source_runs.jsonl",
        DATA_DIR / "authors.jsonl",
        DATA_DIR / "venues.jsonl",
        DATA_DIR / "daily_candidates.jsonl",
        DATA_DIR / "recommendations.jsonl",
        DATA_DIR / "social_items.jsonl",
        DATA_DIR / "trending_items.jsonl",
        DATA_DIR / "taxonomy_assignments.jsonl",
        DATA_DIR / "papers.csv",
        ROOT / "email" / "latest_digest.md",
    ]
    for path in files_to_touch:
        touch(path)


def export_public_csv(papers: list[dict]) -> None:
    rows = []
    for paper in papers:
        rows.append(
            {
                "id": paper.get("id", ""),
                "title": paper.get("title", ""),
                "authors": first_author_name(paper),
                "published_date": paper.get("published_date", ""),
                "source": paper.get("source", ""),
                "venue_or_status": paper.get("venue_or_status", ""),
                "primary_topic": paper.get("primary_topic", ""),
                "secondary_topics": "; ".join(paper.get("secondary_topics", [])),
                "priority": paper.get("priority", ""),
                "fit_score": paper.get("fit_score", ""),
                "interestingness_score": paper.get("interestingness_score", 0.0),
                "paper_url": paper.get("url", ""),
                "pdf_url": paper.get("pdf_url", ""),
                "code_url": paper.get("code_url", ""),
                "project_page": paper.get("project_page", ""),
                "summary_level": paper.get("summary_level", ""),
                "one_sentence_summary": paper.get("one_sentence_summary", ""),
                "why_it_matters": paper.get("why_it_matters", ""),
                "public_note_path": paper.get("public_note_path", ""),
            }
        )
    fieldnames = list(rows[0].keys()) if rows else [
        "id",
        "title",
        "authors",
        "published_date",
        "source",
        "venue_or_status",
        "primary_topic",
        "secondary_topics",
        "priority",
        "fit_score",
        "interestingness_score",
        "paper_url",
        "pdf_url",
        "code_url",
        "project_page",
        "summary_level",
        "one_sentence_summary",
        "why_it_matters",
        "public_note_path",
    ]
    write_csv(DATA_DIR / "papers.csv", rows, fieldnames)


def download_selected_pdfs(selected: list[dict], configs: dict, run_date: date) -> list[dict]:
    limits = configs["limits"]["limits"]
    user_agent = limits.get("user_agent", "ai-paper-radar/0.1")
    timeout = limits.get("http_timeout_seconds", 30)
    pdf_dir = ROOT / "library" / "pdfs" / run_date.isoformat()
    pdf_dir.mkdir(parents=True, exist_ok=True)
    for paper in selected[: limits.get("max_pdf_downloads_per_day", 20)]:
        pdf_url = paper.get("pdf_url", "")
        if not pdf_url:
            continue
        target = pdf_dir / f"{paper['source_ids'].get('arxiv_id') or paper['id']}.pdf"
        if target.exists():
            paper["local_pdf_path"] = str(target.relative_to(ROOT))
            continue
        try:
            request = Request(pdf_url, headers={"User-Agent": user_agent, "Accept": "application/pdf"})
            with urlopen(request, timeout=timeout) as response:
                target.write_bytes(response.read())
            paper["local_pdf_path"] = str(target.relative_to(ROOT))
        except Exception as exc:
            append_jsonl(
                DATA_DIR / "source_runs.jsonl",
                {
                    "source": "pdf_download",
                    "status": "error",
                    "detail": f"{paper.get('title', '')}: {exc}",
                    "item_count": 0,
                    "timestamp": now_iso(),
                    "run_date": run_date.isoformat(),
                    "run_id": os.getenv("AI_PAPER_RADAR_RUN_ID", ""),
                },
            )
    return selected


def write_private_notes(selected: list[dict], run_date: date) -> None:
    notes_dir = ROOT / "library" / "notes" / run_date.isoformat()
    abstracts_dir = ROOT / "library" / "abstracts" / run_date.isoformat()
    notes_dir.mkdir(parents=True, exist_ok=True)
    abstracts_dir.mkdir(parents=True, exist_ok=True)
    for paper in selected:
        slug = paper["id"]
        write_text(
            notes_dir / f"{slug}.md",
            "\n".join(
                [
                    f"# {paper.get('title', '')}",
                    "",
                    f"- Priority: {paper.get('priority', '')}",
                    f"- Topic: {paper.get('primary_topic', '')}",
                    f"- Source: {paper.get('source', '')}",
                    "",
                    paper.get("core_contribution", ""),
                    "",
                    paper.get("main_result_or_claim", ""),
                ]
            )
            + "\n",
        )
        if paper.get("abstract"):
            write_text(abstracts_dir / f"{slug}.txt", paper["abstract"] + "\n")


def _write_seen_ids(papers: list[dict]) -> None:
    seen_ids = sorted({paper["id"] for paper in papers if paper.get("id")})
    write_text(DATA_DIR / "seen_ids.txt", "\n".join(seen_ids) + ("\n" if seen_ids else ""))


def _run_publish_script(push: bool) -> None:
    cmd = ["python", "scripts/publish_github.py"]
    if not push:
        cmd.append("--no-push")
    subprocess.run(cmd, cwd=ROOT, check=True)


def run_daily_pipeline(push: bool = False, run_date: date | None = None, disable_push: bool = False) -> dict:
    initialize_workspace()
    configs = load_all_configs()
    current_date = run_date or today_local()
    run_id = now_iso()
    os.environ["AI_PAPER_RADAR_RUN_ID"] = run_id

    existing_papers = [ensure_schema(paper) for paper in read_jsonl(DATA_DIR / "papers.jsonl")]
    dedupe_reference = [
        paper
        for paper in existing_papers
        if not paper.get("discovered_at", "").startswith(current_date.isoformat())
    ]
    arxiv_candidates, _ = fetch_arxiv_candidates(configs, current_date)
    openreview_candidates, _ = fetch_openreview_candidates(configs)
    candidates = [ensure_schema(paper) for paper in arxiv_candidates + openreview_candidates]
    deduped_candidates, duplicates = deduplicate_papers(
        candidates,
        dedupe_reference,
        configs["limits"]["limits"].get("similarity_dedup_threshold", 0.96),
    )
    social_items, _ = fetch_social_items(configs, current_date)
    gmail_items, _ = fetch_gmail_alerts(configs)
    del gmail_items
    deduped_candidates, _ = enrich_with_semantic_scholar(deduped_candidates, configs)
    deduped_candidates, _ = enrich_with_openalex(deduped_candidates, configs)
    ranked = rank_papers(
        deduped_candidates,
        configs["profile"],
        configs["queries"],
        configs["scoring"],
        configs["taxonomy"],
        current_date,
    )
    selected = [paper for paper in ranked if paper.get("status") == "active"][: configs["limits"]["limits"].get("max_daily_highlights", 10)]
    selected = enrich_selected_from_arxiv(selected, configs)
    selected = [summarize_paper(paper) for paper in selected]
    selected = download_selected_pdfs(selected, configs, current_date)
    selected = [summarize_paper(paper) for paper in selected]
    selected, assignments, _ = update_taxonomy_assignments(selected, configs["taxonomy"], current_date)
    write_private_notes(selected, current_date)

    selected_by_id = {paper["id"]: paper for paper in selected}
    merged_papers: dict[str, dict] = {paper["id"]: paper for paper in existing_papers}
    for paper in ranked:
        merged_papers[paper["id"]] = paper
    for duplicate in duplicates:
        merged_papers[duplicate["id"]] = duplicate
    for paper_id, paper in selected_by_id.items():
        merged_papers[paper_id] = paper
    all_papers = list(merged_papers.values())

    build_catalog(selected, all_papers, configs["taxonomy"], current_date)
    generate_visual_assets(selected, all_papers, configs["taxonomy"], current_date)
    mirror_public_catalog()
    generate_public_readme(selected, all_papers, configs["taxonomy"], current_date)
    source_runs = read_jsonl(DATA_DIR / "source_runs.jsonl")
    generate_digest(selected, all_papers, source_runs, social_items, current_date, run_id=run_id)
    export_public_csv(all_papers)

    write_jsonl(DATA_DIR / "daily_candidates.jsonl", deduped_candidates)
    write_jsonl(DATA_DIR / "recommendations.jsonl", selected)
    write_jsonl(DATA_DIR / "papers.jsonl", all_papers)
    write_jsonl(DATA_DIR / "social_items.jsonl", social_items)
    write_jsonl(DATA_DIR / "trending_items.jsonl", social_items[:10])
    write_jsonl(DATA_DIR / "taxonomy_assignments.jsonl", assignments)
    write_jsonl(DATA_DIR / "authors.jsonl", build_author_index(all_papers))
    write_jsonl(DATA_DIR / "venues.jsonl", build_venue_index(all_papers))
    _write_seen_ids(all_papers)

    errors, warnings = validate_public_outputs()
    validation_report = {
        "run_date": current_date.isoformat(),
        "errors": errors,
        "warnings": warnings,
        "selected_count": len(selected),
        "candidate_count": len(deduped_candidates),
    }
    should_push = push or (configs["github"].get("github", {}).get("auto_push", False) and not disable_push)
    if push or should_push:
        _run_publish_script(push=should_push)
    return validation_report


def cli_main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI Paper Radar daily pipeline.")
    parser.add_argument("--push", action="store_true", help="Allow the GitHub publishing step to push.")
    parser.add_argument("--no-push", action="store_true", help="Disable push even if config enables it.")
    args = parser.parse_args()
    push = args.push and not args.no_push
    report = run_daily_pipeline(push=push, disable_push=args.no_push)
    print(f"Run date: {report['run_date']}")
    print(f"Candidates: {report['candidate_count']}")
    print(f"Selected: {report['selected_count']}")
    print(f"Warnings: {len(report['warnings'])}")
    print(f"Errors: {len(report['errors'])}")
    for error in report["errors"]:
        print(f"ERROR: {error}")
    for warning in report["warnings"]:
        print(f"WARNING: {warning}")

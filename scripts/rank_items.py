#!/usr/bin/env python
import _bootstrap

from paper_radar.analysis import deduplicate_papers, ensure_schema, rank_papers
from paper_radar.config import DATA_DIR, load_all_configs, today_local
from paper_radar.storage import read_jsonl, write_jsonl


def main() -> None:
    configs = load_all_configs()
    existing = [ensure_schema(paper) for paper in read_jsonl(DATA_DIR / "papers.jsonl")]
    candidates = [ensure_schema(paper) for paper in read_jsonl(DATA_DIR / "daily_candidates.jsonl")]
    unique, duplicates = deduplicate_papers(
        candidates,
        existing,
        configs["limits"]["limits"].get("similarity_dedup_threshold", 0.96),
    )
    ranked = rank_papers(
        unique,
        configs["profile"],
        configs["queries"],
        configs["scoring"],
        configs["taxonomy"],
        today_local(),
    )
    selected = [paper for paper in ranked if paper.get("status") == "active"][:10]
    write_jsonl(DATA_DIR / "daily_candidates.jsonl", unique)
    write_jsonl(DATA_DIR / "recommendations.jsonl", selected)
    write_jsonl(DATA_DIR / "papers.jsonl", existing + duplicates + ranked)
    print(f"Ranked {len(unique)} unique candidates and selected {len(selected)} items")


if __name__ == "__main__":
    main()

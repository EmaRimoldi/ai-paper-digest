#!/usr/bin/env python
import _bootstrap

from paper_radar.config import DATA_DIR, today_local
from paper_radar.render import generate_digest
from paper_radar.storage import read_jsonl


def main() -> None:
    selected = read_jsonl(DATA_DIR / "recommendations.jsonl")
    all_papers = read_jsonl(DATA_DIR / "papers.jsonl")
    source_runs = read_jsonl(DATA_DIR / "source_runs.jsonl")
    social_items = read_jsonl(DATA_DIR / "social_items.jsonl")
    generate_digest(selected, all_papers, source_runs, social_items, today_local())
    print("Generated daily and weekly digests")


if __name__ == "__main__":
    main()

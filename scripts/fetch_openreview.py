#!/usr/bin/env python
import _bootstrap

from paper_radar.config import DATA_DIR, load_all_configs
from paper_radar.sources import fetch_openreview_candidates
from paper_radar.storage import read_jsonl, write_jsonl


def main() -> None:
    configs = load_all_configs()
    current = read_jsonl(DATA_DIR / "daily_candidates.jsonl")
    papers, logs = fetch_openreview_candidates(configs)
    del logs
    write_jsonl(DATA_DIR / "daily_candidates.jsonl", current + papers)
    print(f"Added {len(papers)} OpenReview candidates")


if __name__ == "__main__":
    main()

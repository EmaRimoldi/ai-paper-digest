#!/usr/bin/env python
import _bootstrap

from paper_radar.config import load_all_configs, today_local
from paper_radar.sources import fetch_arxiv_candidates
from paper_radar.storage import write_jsonl
from paper_radar.config import DATA_DIR


def main() -> None:
    configs = load_all_configs()
    papers, logs = fetch_arxiv_candidates(configs, today_local())
    del logs
    write_jsonl(DATA_DIR / "daily_candidates.jsonl", papers)
    print(f"Fetched {len(papers)} arXiv candidates")


if __name__ == "__main__":
    main()

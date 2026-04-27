#!/usr/bin/env python
import _bootstrap

from paper_radar.config import DATA_DIR, load_all_configs
from paper_radar.sources import enrich_with_openalex
from paper_radar.storage import read_jsonl, write_jsonl


def main() -> None:
    configs = load_all_configs()
    papers = read_jsonl(DATA_DIR / "daily_candidates.jsonl")
    papers, logs = enrich_with_openalex(papers, configs)
    del logs
    write_jsonl(DATA_DIR / "daily_candidates.jsonl", papers)
    print(f"Enriched {len(papers)} candidates with OpenAlex")


if __name__ == "__main__":
    main()

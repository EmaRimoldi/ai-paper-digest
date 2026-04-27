#!/usr/bin/env python
import _bootstrap

from paper_radar.analysis import update_taxonomy_assignments
from paper_radar.config import DATA_DIR, load_all_configs, today_local
from paper_radar.storage import read_jsonl, write_jsonl


def main() -> None:
    configs = load_all_configs()
    papers = read_jsonl(DATA_DIR / "recommendations.jsonl")
    papers, assignments, proposal = update_taxonomy_assignments(papers, configs["taxonomy"], today_local())
    write_jsonl(DATA_DIR / "recommendations.jsonl", papers)
    write_jsonl(DATA_DIR / "taxonomy_assignments.jsonl", assignments)
    print(f"Updated taxonomy for {len(papers)} papers")
    if proposal:
        print(f"Proposal written to {proposal}")


if __name__ == "__main__":
    main()

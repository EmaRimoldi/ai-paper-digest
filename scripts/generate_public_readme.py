#!/usr/bin/env python
import _bootstrap

from paper_radar.config import DATA_DIR, load_all_configs, today_local
from paper_radar.render import generate_public_readme
from paper_radar.storage import read_jsonl


def main() -> None:
    configs = load_all_configs()
    selected = read_jsonl(DATA_DIR / "recommendations.jsonl")
    all_papers = read_jsonl(DATA_DIR / "papers.jsonl")
    generate_public_readme(selected, all_papers, configs["taxonomy"], today_local())
    print("Updated root README")


if __name__ == "__main__":
    main()

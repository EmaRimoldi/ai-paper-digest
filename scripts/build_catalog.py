#!/usr/bin/env python
import _bootstrap

from paper_radar.config import DATA_DIR, load_all_configs, today_local
from paper_radar.render import build_catalog, mirror_public_catalog
from paper_radar.storage import read_jsonl, write_jsonl


def main() -> None:
    configs = load_all_configs()
    selected = read_jsonl(DATA_DIR / "recommendations.jsonl")
    all_papers = read_jsonl(DATA_DIR / "papers.jsonl")
    selected = build_catalog(selected, all_papers, configs["taxonomy"], today_local())
    mirror_public_catalog()
    write_jsonl(DATA_DIR / "recommendations.jsonl", selected)
    print(f"Built catalog for {len(selected)} selected papers")


if __name__ == "__main__":
    main()

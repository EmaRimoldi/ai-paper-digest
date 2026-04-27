#!/usr/bin/env python
import _bootstrap

from paper_radar.analysis import summarize_paper
from paper_radar.config import DATA_DIR, load_all_configs, today_local
from paper_radar.pipeline import write_private_notes
from paper_radar.sources import enrich_selected_from_arxiv
from paper_radar.storage import read_jsonl, write_jsonl


def main() -> None:
    configs = load_all_configs()
    papers = read_jsonl(DATA_DIR / "recommendations.jsonl")
    papers = enrich_selected_from_arxiv(papers, configs)
    papers = [summarize_paper(paper) for paper in papers]
    write_jsonl(DATA_DIR / "recommendations.jsonl", papers)
    write_private_notes(papers, today_local())
    print(f"Summarized {len(papers)} papers")


if __name__ == "__main__":
    main()

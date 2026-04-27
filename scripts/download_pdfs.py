#!/usr/bin/env python
import _bootstrap

from paper_radar.config import DATA_DIR, load_all_configs, today_local
from paper_radar.pipeline import download_selected_pdfs
from paper_radar.storage import read_jsonl, write_jsonl


def main() -> None:
    configs = load_all_configs()
    papers = read_jsonl(DATA_DIR / "recommendations.jsonl")
    papers = download_selected_pdfs(papers, configs, today_local())
    write_jsonl(DATA_DIR / "recommendations.jsonl", papers)
    downloaded = sum(1 for paper in papers if paper.get("local_pdf_path"))
    print(f"Downloaded or found {downloaded} local PDFs")


if __name__ == "__main__":
    main()

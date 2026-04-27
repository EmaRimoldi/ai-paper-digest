#!/usr/bin/env python
import argparse
import shutil
import subprocess
from pathlib import Path

import _bootstrap

from paper_radar.config import ROOT, today_local
from paper_radar.storage import append_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract local figure candidates from PDFs for private review.")
    parser.add_argument("--date", default=today_local().isoformat(), help="Library PDF date folder to scan.")
    args = parser.parse_args()

    pdf_dir = ROOT / "library" / "pdfs" / args.date
    output_dir = ROOT / "library" / "figure_candidates" / args.date
    output_dir.mkdir(parents=True, exist_ok=True)
    pdfimages = shutil.which("pdfimages")
    if not pdf_dir.exists():
        print(f"No PDFs found in {pdf_dir}")
        return
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        target_prefix = output_dir / pdf_path.stem
        manifest_entry = {
            "pdf": str(pdf_path.relative_to(ROOT)),
            "candidate_prefix": str(target_prefix.relative_to(ROOT)),
            "license_status": "unknown",
            "publish": False,
            "attribution": "",
        }
        if pdfimages:
            subprocess.run([pdfimages, "-png", str(pdf_path), str(target_prefix)], check=False)
        append_jsonl(output_dir / "manifest.jsonl", manifest_entry)
    print(f"Prepared figure candidate manifest in {output_dir}")


if __name__ == "__main__":
    main()

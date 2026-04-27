#!/usr/bin/env python
import _bootstrap

from paper_radar.config import DATA_DIR
from paper_radar.pipeline import export_public_csv
from paper_radar.storage import read_jsonl


def main() -> None:
    export_public_csv(read_jsonl(DATA_DIR / "papers.jsonl"))
    print("Exported public CSV")


if __name__ == "__main__":
    main()

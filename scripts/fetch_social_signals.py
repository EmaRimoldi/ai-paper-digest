#!/usr/bin/env python
import _bootstrap

from paper_radar.config import DATA_DIR, load_all_configs, today_local
from paper_radar.sources import fetch_social_items
from paper_radar.storage import write_jsonl


def main() -> None:
    configs = load_all_configs()
    items, logs = fetch_social_items(configs, today_local())
    del logs
    write_jsonl(DATA_DIR / "social_items.jsonl", items)
    write_jsonl(DATA_DIR / "trending_items.jsonl", items[:10])
    print(f"Fetched {len(items)} social signal items")


if __name__ == "__main__":
    main()

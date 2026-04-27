#!/usr/bin/env python
import _bootstrap

from paper_radar.config import load_all_configs
from paper_radar.sources import fetch_gmail_alerts


def main() -> None:
    configs = load_all_configs()
    items, logs = fetch_gmail_alerts(configs)
    del logs
    print(f"Fetched {len(items)} Gmail alert items")


if __name__ == "__main__":
    main()

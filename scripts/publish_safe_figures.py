#!/usr/bin/env python
import argparse
import shutil
from pathlib import Path

import _bootstrap

from paper_radar.config import ROOT, today_local
from paper_radar.storage import read_jsonl, write_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish only license-safe figures with attribution.")
    parser.add_argument("--date", default=today_local().isoformat(), help="Figure candidate date folder to publish from.")
    args = parser.parse_args()

    source_dir = ROOT / "library" / "figure_candidates" / args.date
    manifest_path = source_dir / "manifest.jsonl"
    target_dir = ROOT / "public" / "assets" / "figures_safe"
    target_dir.mkdir(parents=True, exist_ok=True)
    if not manifest_path.exists():
        print(f"No manifest found at {manifest_path}")
        return
    published = 0
    for item in read_jsonl(manifest_path):
        if not item.get("publish") or item.get("license_status") not in {"cc-by", "cc-by-4.0", "permissive"}:
            continue
        for candidate in source_dir.glob(Path(item["candidate_prefix"]).name + "*"):
            if candidate.is_dir() or candidate.name == "manifest.jsonl":
                continue
            target = target_dir / candidate.name
            shutil.copy2(candidate, target)
            write_text(
                target.with_name(target.name + ".attribution.txt"),
                "\n".join(
                    [
                        f"Source: {item.get('pdf', '')}",
                        f"License: {item.get('license_status', '')}",
                        f"Attribution: {item.get('attribution', '')}",
                    ]
                )
                + "\n",
            )
            published += 1
    print(f"Published {published} safe figures")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
import argparse
import os
import subprocess

import _bootstrap

from paper_radar.config import ROOT, load_all_configs
from paper_radar.validation import validate_public_outputs


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True)


def print_status(label: str) -> None:
    print(label)
    result = subprocess.run(
        ["git", "status", "--short", "--branch"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    print(result.stdout.strip() or "(clean)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Commit and optionally push GitHub-safe outputs.")
    parser.add_argument("--push", action="store_true", help="Push after committing if allowed.")
    parser.add_argument("--no-push", action="store_true", help="Never push from this invocation.")
    args = parser.parse_args()

    configs = load_all_configs()
    github_cfg = configs["github"]["github"]
    errors, warnings = validate_public_outputs()
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print_status("Git status before publish:")
    publish_paths = github_cfg.get("publish_paths", [])
    existing_paths = [path for path in publish_paths if (ROOT / path).exists()]
    if not existing_paths:
        print("No publish paths exist yet")
        return
    subprocess.run(["git", "add", "--", *existing_paths], cwd=ROOT, check=True)
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
        check=False,
    )
    if diff.returncode == 0:
        print("No staged public-safe changes to commit")
        print_status("Git status after publish:")
        return
    if github_cfg.get("auto_commit", True):
        message = f"{github_cfg.get('commit_message_prefix', 'update paper radar')}: {os.getenv('AI_PAPER_RADAR_DATE') or 'daily refresh'}"
        subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
        print(f"Created commit: {message}")
    allow_push = (
        not args.no_push
        and (args.push or github_cfg.get("auto_push", False) or os.getenv("AUTO_PUSH") == "1")
    )
    if allow_push:
        subprocess.run(["git", "push", "origin", github_cfg.get("branch", "main")], cwd=ROOT, check=True)
        print("Push succeeded")
    else:
        print("Push skipped")
    print_status("Git status after publish:")


if __name__ == "__main__":
    main()

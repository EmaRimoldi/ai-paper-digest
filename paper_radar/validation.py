from __future__ import annotations

import csv
import re
from pathlib import Path

from .config import ROOT, public_publish_paths

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9]{20,}",
    r"ghp_[A-Za-z0-9]{20,}",
    r"api[_-]?key",
    r"bearer\s+[A-Za-z0-9._-]{20,}",
]


def _scan_text_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, text, flags=re.I):
            errors.append(f"Potential secret matched `{pattern}` in {path.relative_to(ROOT)}")
    if "library/" in text or "/library/" in text:
        errors.append(f"Public file references local library path: {path.relative_to(ROOT)}")
    return errors


def validate_public_outputs() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for publish_path in public_publish_paths():
        if not publish_path.exists():
            warnings.append(f"Missing publish path: {publish_path.relative_to(ROOT)}")
            continue
        if publish_path.is_file():
            if publish_path.suffix.lower() == ".pdf":
                errors.append(f"PDF found in publish path: {publish_path.relative_to(ROOT)}")
            if publish_path.suffix.lower() in {".md", ".svg", ".csv", ".txt"}:
                errors.extend(_scan_text_file(publish_path))
            continue
        for path in publish_path.rglob("*"):
            if path.is_dir():
                continue
            if path.suffix.lower() == ".pdf":
                errors.append(f"PDF found in publish path: {path.relative_to(ROOT)}")
            if "figures_safe" in path.parts and path.name.endswith(".attribution.txt"):
                continue
            if "figures_safe" in path.parts and path.suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp", ".txt", ".md"}:
                warnings.append(f"Unexpected safe-figure artifact: {path.relative_to(ROOT)}")
            if path.suffix.lower() in {".md", ".svg", ".csv", ".txt"}:
                errors.extend(_scan_text_file(path))
    safe_figures_dir = ROOT / "public" / "assets" / "figures_safe"
    if safe_figures_dir.exists():
        for path in safe_figures_dir.iterdir():
            if path.name.endswith(".attribution.txt") or path.name.endswith(".md"):
                continue
            attribution = path.with_name(path.name + ".attribution.txt")
            if not attribution.exists():
                warnings.append(f"Safe figure missing attribution file: {path.relative_to(ROOT)}")
    papers_csv = ROOT / "data" / "papers.csv"
    if papers_csv.exists():
        with papers_csv.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            if "local_pdf_path" in fieldnames:
                errors.append("Public CSV includes local_pdf_path column")
    return errors, warnings

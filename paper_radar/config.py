from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
LIBRARY_DIR = ROOT / "library"
CATALOG_DIR = ROOT / "catalog"
PUBLIC_DIR = ROOT / "public"
DOCS_DIR = ROOT / "docs"
REPORTS_DIR = ROOT / "reports"
EMAIL_DIR = ROOT / "email"
SCRIPTS_DIR = ROOT / "scripts"
SKILLS_DIR = ROOT / ".agents" / "skills"
DEFAULT_TIMEZONE = "America/New_York"


def repo_path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    data = yaml.safe_load(text)
    return data or {}


def write_yaml(path: Path, value: object) -> None:
    ensure_dir(path.parent)
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )


def load_config(name: str) -> dict:
    return load_yaml(CONFIG_DIR / name)


def load_all_configs() -> dict:
    return {
        "profile": load_config("profile.yml"),
        "sources": load_config("sources.yml"),
        "social_sources": load_config("social_sources.yml"),
        "researchers": load_config("researchers.yml"),
        "queries": load_config("queries.yml"),
        "taxonomy": load_config("taxonomy.yml"),
        "scoring": load_config("scoring.yml"),
        "email": load_config("email.yml"),
        "github": load_config("github.yml"),
        "limits": load_config("limits.yml"),
    }


def local_timezone() -> ZoneInfo:
    return ZoneInfo(os.getenv("AI_PAPER_RADAR_TZ", DEFAULT_TIMEZONE))


def today_local() -> date:
    forced = os.getenv("AI_PAPER_RADAR_DATE")
    if forced:
        return date.fromisoformat(forced)
    return datetime.now(local_timezone()).date()


def now_iso() -> str:
    return datetime.now(local_timezone()).isoformat(timespec="seconds")


def iso_week(run_date: date) -> str:
    year, week, _ = run_date.isocalendar()
    return f"{year}-{week:02d}"


def public_publish_paths() -> list[Path]:
    github_cfg = load_config("github.yml").get("github", {})
    return [repo_path(path) for path in github_cfg.get("publish_paths", [])]


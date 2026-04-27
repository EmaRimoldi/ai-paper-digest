from __future__ import annotations

import shutil
from collections import Counter
from datetime import date
from pathlib import Path

from .analysis import (
    clean_whitespace,
    first_author_name,
    grouped_by_topic,
    note_path_for_paper,
    slugify,
    topic_counts,
    top_topic_rows,
    truncate,
)
from .config import CATALOG_DIR, DOCS_DIR, PUBLIC_DIR, ROOT, iso_week
from .storage import read_text, write_text


def _svg_escape(text: str) -> str:
    return (
        clean_whitespace(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _card_background(index: int) -> tuple[str, str]:
    palettes = [
        ("#0f172a", "#f97316"),
        ("#172554", "#22c55e"),
        ("#1f2937", "#38bdf8"),
        ("#3f1d2e", "#f59e0b"),
        ("#14213d", "#fb7185"),
    ]
    return palettes[index % len(palettes)]


def _catalog_relative_path(path_str: str) -> str:
    if not path_str:
        return ""
    path = Path(path_str)
    if path.parts and path.parts[0] == "catalog":
        path = path.relative_to("catalog")
    return path.as_posix()


def _display_topic(topic: str) -> str:
    return clean_whitespace(topic.replace("_", " ")) or "unknown"


def _summary_source_label(level: str) -> str:
    return {
        "pdf_summary": "local PDF text",
        "abstract_summary": "abstract only",
        "metadata_only": "metadata only",
    }.get(level, level or "unknown")


def _section_summary_rows(paper: dict) -> list[tuple[str, str]]:
    summaries = paper.get("section_summaries") or {}
    result_fallback = clean_whitespace(" ".join(paper.get("key_results", [])[:2])) or paper.get("main_result_or_claim", "")
    rows = [
        ("Abstract", summaries.get("abstract") or paper.get("one_sentence_summary", "")),
        ("Introduction and Problem", summaries.get("introduction") or paper.get("core_contribution", "")),
        ("Method", summaries.get("method") or paper.get("method", "")),
        ("Evaluation and Results", summaries.get("results") or result_fallback),
        ("Limitations", summaries.get("limitations") or paper.get("limitations_or_caveats", "")),
        (
            "Conclusion",
            summaries.get("conclusion")
            or "Conclusion section was not isolated reliably from the local PDF; use the original paper for the final synthesis.",
        ),
    ]
    return [
        (heading, clean_whitespace(text) or "Section summary unavailable from the current extraction.")
        for heading, text in rows
    ]


def _paper_page_lines(paper: dict, run_date: date) -> list[str]:
    first_author = first_author_name(paper) or "unknown"
    published = paper.get("published_date") or run_date.isoformat()
    secondary_topics = ", ".join(_display_topic(topic) for topic in paper.get("secondary_topics", [])) or "none"
    lines = [
        f"# {paper.get('title', '')}",
        "",
        f"*{first_author} · {published} · {_display_topic(paper.get('primary_topic', ''))} · {paper.get('priority', 'unknown')}*",
        "",
        _links_line(paper),
        "",
        "## TL;DR",
        "",
        clean_whitespace(paper.get("one_sentence_summary", "")) or "Summary based on abstract/metadata only.",
        "",
        "## Main Contribution",
        "",
        clean_whitespace(paper.get("core_contribution", "")) or "Summary based on abstract/metadata only.",
        "",
        "## Main Result",
        "",
        clean_whitespace(paper.get("main_result_or_claim", "")) or "unknown",
        "",
        "## Method in Brief",
        "",
        clean_whitespace(paper.get("method", "")) or "unknown",
        "",
        "## Summary by Section",
        "",
    ]
    for heading, text in _section_summary_rows(paper):
        lines.extend([f"### {heading}", "", text, ""])
    lines.extend(
        [
            "## Caveats",
            "",
            clean_whitespace(paper.get("limitations_or_caveats", "")) or "Summary based on abstract/metadata only.",
            "",
            "## Quick Facts",
            "",
            f"- First author: {first_author}",
            f"- Primary topic: {_display_topic(paper.get('primary_topic', ''))}",
            f"- Secondary topics: {secondary_topics}",
            f"- Fit: {paper.get('fit_score', 'unknown')}",
            f"- Summary source: {_summary_source_label(paper.get('summary_level', ''))}",
        ]
    )
    return lines


def generate_visual_assets(top_papers: list[dict], all_papers: list[dict], taxonomy: dict, run_date: date) -> None:
    assets_dir = PUBLIC_DIR / "assets"
    topic_cards_dir = assets_dir / "topic_cards"
    paper_cards_dir = assets_dir / "paper_cards"
    for directory in (assets_dir, topic_cards_dir, paper_cards_dir, assets_dir / "figures_safe"):
        directory.mkdir(parents=True, exist_ok=True)
    topic_summary = topic_counts(all_papers)
    hero_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#111827"/>
      <stop offset="50%" stop-color="#7c2d12"/>
      <stop offset="100%" stop-color="#0f766e"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <circle cx="1030" cy="120" r="160" fill="rgba(255,255,255,0.07)"/>
  <circle cx="140" cy="520" r="110" fill="rgba(255,255,255,0.06)"/>
  <rect x="70" y="82" width="190" height="34" rx="17" fill="#f97316"/>
  <text x="95" y="105" fill="#fff7ed" font-size="18" font-family="Georgia, serif">Daily Research Radar</text>
  <text x="70" y="210" fill="#f8fafc" font-size="72" font-weight="700" font-family="Georgia, serif">AI Paper Radar</text>
  <text x="70" y="280" fill="#e2e8f0" font-size="30" font-family="'Trebuchet MS', sans-serif">Noise-to-signal monitoring for modern AI research.</text>
  <text x="70" y="334" fill="#cbd5e1" font-size="24" font-family="'Trebuchet MS', sans-serif">Top 10 picks, short notes, topic tracking, and public-safe publishing.</text>
  <text x="70" y="498" fill="#fed7aa" font-size="22" font-family="'Trebuchet MS', sans-serif">Updated {run_date.isoformat()}</text>
  <text x="70" y="536" fill="#fef3c7" font-size="22" font-family="'Trebuchet MS', sans-serif">I outsource the noise, not the thinking.</text>
</svg>"""
    write_text(assets_dir / "hero.svg", hero_svg)

    topic_boxes = []
    x, y = 80, 110
    for index, (slug, meta) in enumerate(taxonomy.get("topics", {}).items()):
        count = topic_summary.get(slug, 0)
        fill, accent = _card_background(index)
        topic_boxes.append(
            f"""
  <rect x="{x}" y="{y}" width="310" height="92" rx="18" fill="{fill}" stroke="{accent}" stroke-width="3"/>
  <text x="{x + 18}" y="{y + 34}" fill="#f8fafc" font-size="24" font-family="Georgia, serif">{_svg_escape(meta.get('title', slug.replace('_', ' ').title()))}</text>
  <text x="{x + 18}" y="{y + 66}" fill="#cbd5e1" font-size="17" font-family="'Trebuchet MS', sans-serif">{count} tracked papers</text>
"""
        )
        x += 350
        if x > 780:
            x = 80
            y += 125
    topic_map_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">
  <rect width="1200" height="720" fill="#fffaf2"/>
  <text x="80" y="62" fill="#1f2937" font-size="46" font-weight="700" font-family="Georgia, serif">Topic Map</text>
  <text x="80" y="94" fill="#6b7280" font-size="22" font-family="'Trebuchet MS', sans-serif">The public catalog groups papers by stable topic slugs, not by daily hype.</text>
  {''.join(topic_boxes)}
</svg>"""
    write_text(assets_dir / "topic_map.svg", topic_map_svg)

    top_lines = []
    for index, paper in enumerate(top_papers[:10], start=1):
        top_lines.append(
            f'<text x="80" y="{110 + index * 45}" fill="#f8fafc" font-size="24" font-family="Georgia, serif">{index}. {_svg_escape(truncate(paper.get("title", ""), 74))}</text>'
        )
        top_lines.append(
            f'<text x="95" y="{132 + index * 45}" fill="#cbd5e1" font-size="16" font-family="Trebuchet MS, sans-serif">{_svg_escape(paper.get("primary_topic", "").replace("_", " "))} · {_svg_escape(paper.get("priority", ""))}</text>'
        )
    daily_top10_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="780" viewBox="0 0 1200 780">
  <rect width="1200" height="780" fill="#111827"/>
  <rect x="55" y="55" width="1090" height="670" rx="28" fill="#1f2937" stroke="#f97316" stroke-width="4"/>
  <text x="80" y="105" fill="#fff7ed" font-size="44" font-family="Georgia, serif">Top 10 Most Interesting Papers</text>
  <text x="80" y="138" fill="#fdba74" font-size="20" font-family="Trebuchet MS, sans-serif">{run_date.isoformat()}</text>
  {''.join(top_lines)}
</svg>"""
    write_text(assets_dir / "daily_top10.svg", daily_top10_svg)

    for index, (slug, meta) in enumerate(taxonomy.get("topics", {}).items()):
        fill, accent = _card_background(index)
        count = topic_summary.get(slug, 0)
        topic_card = f"""<svg xmlns="http://www.w3.org/2000/svg" width="720" height="380" viewBox="0 0 720 380">
  <rect width="720" height="380" rx="28" fill="{fill}"/>
  <rect x="24" y="24" width="672" height="332" rx="22" fill="none" stroke="{accent}" stroke-width="3"/>
  <text x="44" y="86" fill="#f8fafc" font-size="38" font-family="Georgia, serif">{_svg_escape(meta.get('title', slug))}</text>
  <text x="44" y="126" fill="#cbd5e1" font-size="20" font-family="Trebuchet MS, sans-serif">{_svg_escape(meta.get('description', ''))}</text>
  <text x="44" y="330" fill="#fdba74" font-size="24" font-family="Trebuchet MS, sans-serif">{count} tracked papers</text>
</svg>"""
        write_text(topic_cards_dir / f"{slug}.svg", topic_card)

    for index, paper in enumerate(top_papers[:10]):
        fill, accent = _card_background(index)
        card = f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="420" viewBox="0 0 960 420">
  <rect width="960" height="420" rx="28" fill="{fill}"/>
  <rect x="24" y="24" width="912" height="372" rx="24" fill="none" stroke="{accent}" stroke-width="3"/>
  <text x="48" y="74" fill="#fff7ed" font-size="18" font-family="Trebuchet MS, sans-serif">{run_date.isoformat()} · {_svg_escape(paper.get('priority', ''))}</text>
  <text x="48" y="136" fill="#f8fafc" font-size="34" font-family="Georgia, serif">{_svg_escape(truncate(paper.get('title', ''), 96))}</text>
  <text x="48" y="184" fill="#cbd5e1" font-size="20" font-family="Trebuchet MS, sans-serif">{_svg_escape(paper.get('primary_topic', '').replace('_', ' ').title())}</text>
  <text x="48" y="240" fill="#e5e7eb" font-size="22" font-family="Trebuchet MS, sans-serif">{_svg_escape(truncate(paper.get('one_sentence_summary') or paper.get('core_contribution') or paper.get('title', ''), 120))}</text>
  <text x="48" y="340" fill="#fdba74" font-size="20" font-family="Trebuchet MS, sans-serif">{_svg_escape(truncate(paper.get('why_it_matters', ''), 92))}</text>
</svg>"""
        slug = slugify(paper["title"])
        write_text(paper_cards_dir / f"{slug}.svg", card)


def _links_line(paper: dict) -> str:
    links = []
    if paper.get("url"):
        links.append(f"[paper]({paper['url']})")
    if paper.get("pdf_url"):
        links.append(f"[pdf]({paper['pdf_url']})")
    if paper.get("code_url"):
        links.append(f"[code]({paper['code_url']})")
    elif paper.get("project_page"):
        links.append(f"[project]({paper['project_page']})")
    return " / ".join(links) or "n/a"


def build_catalog(top_papers: list[dict], all_papers: list[dict], taxonomy: dict, run_date: date) -> list[dict]:
    run_dir = CATALOG_DIR / "papers" / run_date.isoformat()
    run_dir.mkdir(parents=True, exist_ok=True)
    docs_run_dir = DOCS_DIR / "papers" / run_date.isoformat()
    docs_run_dir.mkdir(parents=True, exist_ok=True)
    for paper in top_papers[:10]:
        slug = slugify(paper["title"])
        page_lines = _paper_page_lines(paper, run_date)
        note_path = note_path_for_paper(run_date, paper)
        write_text(note_path, "\n".join(page_lines) + "\n")
        relative_note = note_path.relative_to(ROOT).as_posix()
        paper["public_note_path"] = relative_note
        paper["public_card_path"] = ""
        write_text(docs_run_dir / f"{slug}.md", "\n".join(page_lines) + "\n")

    grouped = grouped_by_topic(all_papers)
    for topic_slug, meta in taxonomy.get("topics", {}).items():
        topic_dir = CATALOG_DIR / "topics" / topic_slug
        topic_dir.mkdir(parents=True, exist_ok=True)
        topic_title = meta.get("title", topic_slug.replace("_", " ").title())
        publishable_rows = [paper for paper in grouped.get(topic_slug, []) if paper.get("public_note_path")]
        rows = top_topic_rows(publishable_rows, topic_slug, limit=8)
        table = ["| Date | Paper | Why interesting | Links |", "|---|---|---|---|"]
        for paper in rows:
            paper_link = paper.get("public_note_path", "")
            note_rel = f"../../{_catalog_relative_path(paper_link)}" if paper_link else ""
            label = f"[{paper.get('title', '')}]({note_rel})" if note_rel else paper.get("title", "")
            table.append(
                f"| {paper.get('published_date') or run_date.isoformat()} | {label} | {truncate(paper.get('why_it_matters', ''), 84)} | {_links_line(paper)} |"
            )
        content = "\n".join(
            [
                f"# {topic_title}",
                "",
                meta.get("description", "Short description pending."),
                "",
                "## Latest highlights",
                "",
                *table,
                "",
                "## Best recent papers",
                "",
                "Use the table above as the rolling shortlist for this topic.",
                "",
                "## Subtopics",
                "",
                ", ".join(meta.get("subtopics", [])) or "unknown",
                "",
                "## Notes",
                "",
                "Pages are generated automatically from the ranked paper set.",
            ]
        )
        write_text(topic_dir / "README.md", content + "\n")
        docs_topic_dir = DOCS_DIR / "topics" / topic_slug
        docs_topic_dir.mkdir(parents=True, exist_ok=True)
        write_text(docs_topic_dir / "README.md", content + "\n")

    topic_index_lines = ["# Catalog Index", "", f"Updated: {run_date.isoformat()}", "", "## Topics", ""]
    for topic_slug, meta in taxonomy.get("topics", {}).items():
        topic_index_lines.append(f"- [{meta.get('title', topic_slug)}](topics/{topic_slug}/README.md)")
    topic_index_lines.extend(["", "## Latest Papers", ""])
    for paper in top_papers[:10]:
        path = _catalog_relative_path(paper.get("public_note_path", ""))
        topic_index_lines.append(f"- [{paper['title']}]({path})")
    index_content = "\n".join(topic_index_lines) + "\n"
    write_text(CATALOG_DIR / "index.md", index_content)
    write_text(CATALOG_DIR / "README.md", index_content)
    write_text(DOCS_DIR / "index.md", index_content)
    return top_papers


def _replace_marker_block(content: str, marker: str, replacement: str) -> str:
    token = f"<!-- AUTO-GENERATED:{marker} -->"
    pattern = rf"{re_escape(token)}(?:.*?)(?=(\n## |\Z))"
    if token not in content:
        return content
    return __import__("re").sub(pattern, token + "\n\n" + replacement.strip() + "\n", content, flags=__import__("re").S)


def re_escape(text: str) -> str:
    return __import__("re").escape(text)


def generate_public_readme(top_papers: list[dict], all_papers: list[dict], taxonomy: dict, run_date: date) -> None:
    readme_path = ROOT / "README.md"
    content = read_text(readme_path)
    metadata_block = "\n".join(
        [
            f"Last updated: `{run_date.isoformat()}`",
            f"Papers tracked: `{len(all_papers)}`",
        ]
    )
    top10_lines = []
    for index, paper in enumerate(top_papers[:10], start=1):
        note_link = paper.get("public_note_path", "")
        link = note_link
        label = f"[{paper.get('title', '')}]({link})" if link else paper.get("title", "")
        top10_lines.append(
            f"{index}. {label} — {paper.get('primary_topic', '').replace('_', ' ')}. {paper.get('one_sentence_summary', '')}"
        )
    topic_links = []
    for topic_slug, meta in taxonomy.get("topics", {}).items():
        count = Counter(item.get("primary_topic") for item in all_papers).get(topic_slug, 0)
        topic_links.append(
            f"- [{meta.get('title', topic_slug)}](catalog/topics/{topic_slug}/README.md) — {count} tracked papers"
        )
    content = _replace_marker_block(content, "RUN_METADATA", metadata_block)
    content = _replace_marker_block(content, "DAILY_TOP10", "\n".join(top10_lines))
    content = _replace_marker_block(content, "TOPIC_INDEX", "\n".join(topic_links))
    write_text(readme_path, content)


def generate_digest(
    top_papers: list[dict],
    all_papers: list[dict],
    source_runs: list[dict],
    social_items: list[dict],
    run_date: date,
    run_id: str = "",
) -> None:
    subject = f"Subject: AI Paper Radar — Top 10 — {run_date.isoformat()}"
    lines = [
        subject,
        "",
        f"# AI Paper Radar — {run_date.isoformat()}",
        "",
        "## Top 10 most interesting",
        "",
    ]
    for index, paper in enumerate(top_papers[:10], start=1):
        lines.extend(
            [
                f"{index}. {paper.get('title', '')}",
                f"   - Topic: {paper.get('primary_topic', '').replace('_', ' ')}",
                f"   - Links: {_links_line(paper)}",
                f"   - TL;DR: {paper.get('one_sentence_summary', '')}",
                f"   - Key result: {paper.get('main_result_or_claim', '')}",
                f"   - Why interesting: {paper.get('why_it_matters', '')}",
                "",
            ]
        )
    lines.extend(["## Social/researcher signals", ""])
    if social_items:
        for item in social_items[:5]:
            lines.append(f"- {item.get('source', 'signal')}: {item.get('title', '')} — {item.get('url', '')}")
    else:
        lines.append("- No verified public research feeds were configured for this run.")
    lines.extend(["", "## New catalog pages", ""])
    for paper in top_papers[:10]:
        lines.append(f"- {paper.get('public_note_path', '')}")
    lines.extend(["", "## Source run log", ""])
    filtered_source_runs = [
        entry for entry in source_runs if not run_id or entry.get("run_id") == run_id
    ] or source_runs[-12:]
    for entry in filtered_source_runs[-12:]:
        lines.append(f"- {entry.get('source')}: {entry.get('status')} — {entry.get('detail')}")
    report_text = "\n".join(lines) + "\n"
    write_text(ROOT / "reports" / "daily" / f"{run_date.isoformat()}.md", report_text)
    write_text(ROOT / "email" / "latest_digest.md", report_text)

    week = iso_week(run_date)
    week_lines = [
        f"# AI Paper Radar — Weekly Summary — {week}",
        "",
        "## Top 10 papers of the week",
        "",
    ]
    for paper in top_papers[:10]:
        week_lines.append(f"- {paper.get('title', '')} ({paper.get('primary_topic', '').replace('_', ' ')})")
    counts = topic_counts(all_papers)
    week_lines.extend(["", "## Most active topics", ""])
    for topic_slug, count in counts.items():
        week_lines.append(f"- {topic_slug.replace('_', ' ')}: {count}")
    week_lines.extend(
        [
            "",
            "## Emerging trends",
            "",
            "- Recent papers cluster around the leading topics listed above.",
            "",
            "## Strongest technical papers",
            "",
        ]
    )
    for paper in top_papers[:3]:
        week_lines.append(f"- {paper.get('title', '')}")
    week_lines.extend(["", "## Notes", "", "Generated automatically from the tracked paper set."])
    weekly_text = "\n".join(week_lines) + "\n"
    write_text(ROOT / "reports" / "weekly" / f"{week}.md", weekly_text)
    write_text(CATALOG_DIR / "weekly" / f"{week}.md", weekly_text)


def mirror_public_catalog() -> None:
    docs_assets = DOCS_DIR / "assets"
    docs_assets.mkdir(parents=True, exist_ok=True)
    public_assets = PUBLIC_DIR / "assets"
    if not public_assets.exists():
        return
    for item in public_assets.iterdir():
        target = docs_assets / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)

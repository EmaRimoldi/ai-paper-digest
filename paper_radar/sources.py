from __future__ import annotations

import json
import os
import re
import time
from datetime import date
from html import unescape
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from .analysis import clean_whitespace, ensure_schema, stable_paper_id, strip_tags
from .config import DATA_DIR, now_iso, today_local
from .storage import append_jsonl


def _http_get(url: str, user_agent: str, timeout: int, accept: str = "*/*") -> bytes:
    request = Request(url, headers={"User-Agent": user_agent, "Accept": accept})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def _log_source_run(source: str, status: str, detail: str, item_count: int = 0) -> dict:
    payload = {
        "source": source,
        "status": status,
        "detail": detail,
        "item_count": item_count,
        "timestamp": now_iso(),
        "run_date": today_local().isoformat(),
        "run_id": os.getenv("AI_PAPER_RADAR_RUN_ID", ""),
    }
    append_jsonl(DATA_DIR / "source_runs.jsonl", payload)
    return payload


def _extract_authors(block: str) -> list[str]:
    return [strip_tags(match) for match in re.findall(r">([^<]+)</a>", block)]


def _extract_title(block: str) -> str:
    match = re.search(r"Title:</span>\s*(.*?)\s*</div>", block, re.S)
    return strip_tags(match.group(1)) if match else ""


def _extract_subjects(block: str) -> list[str]:
    match = re.search(r"Subjects:</span>\s*(.*?)\s*</div>", block, re.S)
    if not match:
        return []
    content = strip_tags(match.group(1))
    return [clean_whitespace(part) for part in content.split(";") if clean_whitespace(part)]


def _extract_recent_entries(html_text: str, category: str, limit: int) -> list[dict]:
    entries: list[dict] = []
    for match in re.finditer(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", html_text, re.S):
        dt_block, dd_block = match.groups()
        abs_match = re.search(r'href\s*=\s*"/abs/([^"]+)"', dt_block)
        if not abs_match:
            continue
        arxiv_id = abs_match.group(1)
        pdf_match = re.search(r'href="/pdf/([^"]+)"', dt_block)
        paper = ensure_schema(
            {
                "source": "arxiv",
                "source_ids": {"arxiv_id": arxiv_id},
                "title": _extract_title(dd_block),
                "authors": _extract_authors(dd_block),
                "categories": _extract_subjects(dd_block) or [category],
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "pdf_url": f"https://arxiv.org/pdf/{pdf_match.group(1)}.pdf" if pdf_match else f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                "venue_or_status": "arXiv preprint",
            }
        )
        paper["id"] = stable_paper_id(paper)
        entries.append(paper)
        if len(entries) >= limit:
            break
    return entries


def _fetch_arxiv_api(categories: list[str], max_results: int, user_agent: str, timeout: int) -> list[dict]:
    query = " OR ".join(f"cat:{category}" for category in categories)
    params = urlencode(
        {
            "search_query": query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": str(max_results),
        }
    )
    url = f"https://export.arxiv.org/api/query?{params}"
    payload = _http_get(url, user_agent=user_agent, timeout=timeout, accept="application/atom+xml")
    root = ET.fromstring(payload)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    papers: list[dict] = []
    for entry in root.findall("atom:entry", namespace):
        links = {item.attrib.get("title", ""): item.attrib.get("href", "") for item in entry.findall("atom:link", namespace)}
        categories_found = [item.attrib.get("term", "") for item in entry.findall("atom:category", namespace)]
        paper = ensure_schema(
            {
                "source": "arxiv",
                "source_ids": {
                    "arxiv_id": clean_whitespace(entry.findtext("atom:id", default="", namespaces=namespace)).split("/")[-1],
                },
                "title": clean_whitespace(entry.findtext("atom:title", default="", namespaces=namespace)),
                "authors": [
                    clean_whitespace(author.findtext("atom:name", default="", namespaces=namespace))
                    for author in entry.findall("atom:author", namespace)
                ],
                "abstract": clean_whitespace(entry.findtext("atom:summary", default="", namespaces=namespace)),
                "published_date": clean_whitespace(entry.findtext("atom:published", default="", namespaces=namespace))[:10],
                "updated_date": clean_whitespace(entry.findtext("atom:updated", default="", namespaces=namespace))[:10],
                "categories": [category for category in categories_found if category],
                "url": clean_whitespace(entry.findtext("atom:id", default="", namespaces=namespace)),
                "pdf_url": links.get("pdf", ""),
                "venue_or_status": "arXiv preprint",
            }
        )
        paper["id"] = stable_paper_id(paper)
        papers.append(paper)
    return papers


def fetch_arxiv_candidates(configs: dict, run_date: date) -> tuple[list[dict], list[dict]]:
    limits = configs["limits"]["limits"]
    sources = configs["sources"]["sources"]
    categories = configs["queries"].get("arxiv_categories", [])
    user_agent = limits.get("user_agent", "ai-paper-radar/0.1")
    timeout = limits.get("http_timeout_seconds", 30)
    max_per_category = limits.get("max_candidates_per_category", 12)
    max_results = limits.get("max_candidates_per_run", 80)
    logs: list[dict] = []
    if not sources.get("arxiv", {}).get("enabled", True):
        return [], [_log_source_run("arxiv", "skipped", "arXiv disabled in config", 0)]
    try:
        papers = _fetch_arxiv_api(categories, max_results=max_results, user_agent=user_agent, timeout=timeout)
        logs.append(_log_source_run("arxiv", "ok", "Fetched via arXiv API", len(papers)))
        return papers, logs
    except Exception as exc:
        logs.append(_log_source_run("arxiv", "fallback", f"API fetch failed: {exc}", 0))
    papers: list[dict] = []
    recent_template = sources["arxiv"]["recent_page_url_template"]
    for category in categories:
        url = recent_template.format(category=category)
        try:
            html_text = _http_get(url, user_agent=user_agent, timeout=timeout, accept="text/html").decode("utf-8", "replace")
            extracted = _extract_recent_entries(html_text, category, max_per_category)
            papers.extend(extracted)
            logs.append(_log_source_run("arxiv_recent_page", "ok", f"Fetched {category}", len(extracted)))
            time.sleep(limits.get("request_pause_seconds", 0.2))
        except Exception as exc:
            logs.append(_log_source_run("arxiv_recent_page", "error", f"{category}: {exc}", 0))
    unique_by_id: dict[str, dict] = {}
    for paper in papers:
        unique_by_id[paper["id"]] = paper
    unique = list(unique_by_id.values())[:max_results]
    return unique, logs


def fetch_arxiv_abstract(arxiv_id: str, user_agent: str, timeout: int) -> dict:
    url = f"https://arxiv.org/abs/{arxiv_id}"
    html_text = _http_get(url, user_agent=user_agent, timeout=timeout, accept="text/html").decode("utf-8", "replace")
    abstract_match = re.search(r"<blockquote class=\"abstract mathjax\">\s*<span class=\"descriptor\">Abstract:</span>(.*?)</blockquote>", html_text, re.S)
    history_match = re.search(r"Submitted\s+on\s+(\d+\s+\w+\s+\d{4})", html_text)
    title_match = re.search(r"<title>(.*?)</title>", html_text, re.S)
    dateline_match = re.search(r"<div class=\"dateline\">(.*?)</div>", html_text, re.S)
    abstract = strip_tags(abstract_match.group(1)) if abstract_match else ""
    submitted = ""
    if history_match:
        submitted = _parse_human_date(history_match.group(1))
    elif dateline_match:
        parsed = re.search(r"(\d+\s+\w+\s+\d{4})", strip_tags(dateline_match.group(1)))
        if parsed:
            submitted = _parse_human_date(parsed.group(1))
    return {
        "title": strip_tags(title_match.group(1).split("arXiv.org", 1)[0]) if title_match else "",
        "abstract": abstract,
        "published_date": submitted,
    }


def _parse_human_date(raw_date: str) -> str:
    from datetime import datetime

    cleaned = clean_whitespace(raw_date)
    for fmt in ("%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(cleaned, fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def enrich_selected_from_arxiv(selected: list[dict], configs: dict) -> list[dict]:
    limits = configs["limits"]["limits"]
    user_agent = limits.get("user_agent", "ai-paper-radar/0.1")
    timeout = limits.get("http_timeout_seconds", 30)
    for paper in selected:
        arxiv_id = paper.get("source_ids", {}).get("arxiv_id", "")
        if not arxiv_id:
            continue
        if paper.get("abstract") and paper.get("published_date"):
            continue
        try:
            details = fetch_arxiv_abstract(arxiv_id, user_agent=user_agent, timeout=timeout)
            if details.get("abstract") and not paper.get("abstract"):
                paper["abstract"] = details["abstract"]
            if details.get("published_date") and not paper.get("published_date"):
                paper["published_date"] = details["published_date"]
            if details.get("title") and not paper.get("title"):
                paper["title"] = details["title"]
            paper["last_checked_at"] = now_iso()
            time.sleep(limits.get("request_pause_seconds", 0.2))
        except Exception as exc:
            _log_source_run("arxiv_abs", "error", f"{arxiv_id}: {exc}", 0)
    return selected


def fetch_openreview_candidates(configs: dict) -> tuple[list[dict], list[dict]]:
    limits = configs["limits"]["limits"]
    user_agent = limits.get("user_agent", "ai-paper-radar/0.1")
    timeout = limits.get("http_timeout_seconds", 30)
    openreview_cfg = configs["sources"]["sources"].get("openreview", {})
    venues = openreview_cfg.get("venues", [])
    if not openreview_cfg.get("enabled", True):
        return [], [_log_source_run("openreview", "skipped", "OpenReview disabled in config", 0)]
    if not venues:
        return [], [_log_source_run("openreview", "skipped", "No OpenReview venues configured", 0)]
    papers: list[dict] = []
    logs: list[dict] = []
    for venue in venues:
        url = f"{openreview_cfg['base_url']}/notes?invitation={quote(venue, safe='')}&limit=25&offset=0"
        try:
            payload = json.loads(_http_get(url, user_agent=user_agent, timeout=timeout, accept="application/json"))
            notes = payload.get("notes", [])
            for note in notes:
                content = note.get("content", {})
                authors = content.get("authors", [])
                abstract = content.get("abstract", "")
                paper = ensure_schema(
                    {
                        "source": "openreview",
                        "source_ids": {"openreview_id": note.get("id", "")},
                        "title": content.get("title", ""),
                        "authors": authors if isinstance(authors, list) else [],
                        "abstract": abstract if isinstance(abstract, str) else "",
                        "url": f"https://openreview.net/forum?id={note.get('forum') or note.get('id', '')}",
                        "venue_or_status": venue,
                    }
                )
                papers.append(paper)
            logs.append(_log_source_run("openreview", "ok", f"Fetched {venue}", len(notes)))
        except Exception as exc:
            logs.append(_log_source_run("openreview", "error", f"{venue}: {exc}", 0))
    return papers, logs


def _best_effort_json(url: str, user_agent: str, timeout: int) -> dict | None:
    try:
        return json.loads(_http_get(url, user_agent=user_agent, timeout=timeout, accept="application/json"))
    except Exception:
        return None


def enrich_with_semantic_scholar(papers: list[dict], configs: dict) -> tuple[list[dict], list[dict]]:
    limits = configs["limits"]["limits"]
    timeout = limits.get("http_timeout_seconds", 30)
    user_agent = limits.get("user_agent", "ai-paper-radar/0.1")
    max_enrich = limits.get("max_enrich_candidates", 50)
    logs: list[dict] = []
    enriched_count = 0
    for paper in papers[:max_enrich]:
        title = paper.get("title", "")
        if not title:
            continue
        query = quote(title)
        url = (
            "https://api.semanticscholar.org/graph/v1/paper/search/match"
            f"?query={query}&fields=title,url,abstract,venue,year,citationCount,"
            "influentialCitationCount,authors,externalIds,openAccessPdf"
        )
        payload = _best_effort_json(url, user_agent=user_agent, timeout=timeout)
        if not payload:
            continue
        data = (payload.get("data") or [None])[0]
        if not data:
            continue
        if clean_whitespace(data.get("title", "")).lower() != title.lower() and len(title) > 10:
            paper_similarity = clean_whitespace(data.get("title", ""))
            if paper_similarity and paper_similarity.lower() not in title.lower() and title.lower() not in paper_similarity.lower():
                continue
        paper["source_ids"]["semantic_scholar_id"] = data.get("paperId", paper["source_ids"].get("semantic_scholar_id", ""))
        if data.get("abstract") and not paper.get("abstract"):
            paper["abstract"] = clean_whitespace(data["abstract"])
        if data.get("url") and not paper.get("url"):
            paper["url"] = data["url"]
        if data.get("venue") and not paper.get("venue_or_status"):
            paper["venue_or_status"] = data["venue"]
        if data.get("citationCount") is not None:
            paper["citation_count"] = data["citationCount"]
        if data.get("influentialCitationCount") is not None:
            paper["influential_citation_count"] = data["influentialCitationCount"]
        open_access = data.get("openAccessPdf") or {}
        if open_access.get("url") and not paper.get("pdf_url"):
            paper["pdf_url"] = open_access["url"]
        external_ids = data.get("externalIds") or {}
        if external_ids.get("DOI"):
            paper["source_ids"]["doi"] = external_ids["DOI"]
        authors = [clean_whitespace(author.get("name", "")) for author in data.get("authors", [])]
        if authors and not paper.get("authors"):
            paper["authors"] = [author for author in authors if author]
        paper["last_checked_at"] = now_iso()
        enriched_count += 1
        time.sleep(limits.get("request_pause_seconds", 0.2))
    logs.append(_log_source_run("semantic_scholar", "ok", "Semantic Scholar enrichment completed", enriched_count))
    return papers, logs


def enrich_with_openalex(papers: list[dict], configs: dict) -> tuple[list[dict], list[dict]]:
    limits = configs["limits"]["limits"]
    timeout = limits.get("http_timeout_seconds", 30)
    user_agent = limits.get("user_agent", "ai-paper-radar/0.1")
    max_enrich = limits.get("max_enrich_candidates", 50)
    logs: list[dict] = []
    enriched_count = 0
    for paper in papers[:max_enrich]:
        title = paper.get("title", "")
        if not title:
            continue
        url = f"https://api.openalex.org/works?search={quote(title)}&per-page=1"
        payload = _best_effort_json(url, user_agent=user_agent, timeout=timeout)
        if not payload:
            continue
        results = payload.get("results") or []
        if not results:
            continue
        item = results[0]
        matched_title = clean_whitespace(item.get("display_name", ""))
        if matched_title and matched_title.lower() != title.lower() and title.lower() not in matched_title.lower():
            continue
        paper["source_ids"]["openalex_id"] = item.get("id", "").split("/")[-1]
        doi = item.get("doi", "")
        if doi and not paper["source_ids"].get("doi"):
            paper["source_ids"]["doi"] = doi.replace("https://doi.org/", "")
        if item.get("publication_date") and not paper.get("published_date"):
            paper["published_date"] = item["publication_date"]
        if item.get("primary_location", {}).get("source", {}).get("display_name") and not paper.get("venue_or_status"):
            paper["venue_or_status"] = item["primary_location"]["source"]["display_name"]
        institutions = []
        for authorship in item.get("authorships", []):
            for institution in authorship.get("institutions", []):
                name = clean_whitespace(institution.get("display_name", ""))
                if name:
                    institutions.append(name)
        if institutions and not paper.get("institutions"):
            paper["institutions"] = sorted(set(institutions))
        paper["last_checked_at"] = now_iso()
        enriched_count += 1
        time.sleep(limits.get("request_pause_seconds", 0.2))
    logs.append(_log_source_run("openalex", "ok", "OpenAlex enrichment completed", enriched_count))
    return papers, logs


def fetch_social_items(configs: dict, run_date: date) -> tuple[list[dict], list[dict]]:
    del run_date
    limits = configs["limits"]["limits"]
    timeout = limits.get("http_timeout_seconds", 30)
    user_agent = limits.get("user_agent", "ai-paper-radar/0.1")
    feeds = configs["social_sources"].get("social_sources", {}).get("rss_feeds", [])
    max_items = configs["social_sources"].get("social_sources", {}).get("max_items_per_feed", 15)
    if not feeds:
        return [], [_log_source_run("social_signals", "skipped", "No verified RSS feeds configured", 0)]
    items: list[dict] = []
    logs: list[dict] = []
    for feed in feeds:
        try:
            raw = _http_get(feed["url"], user_agent=user_agent, timeout=timeout, accept="application/rss+xml")
            root = ET.fromstring(raw)
            channel = root.find("channel")
            count = 0
            if channel is None:
                continue
            for item in channel.findall("item"):
                entry = {
                    "id": stable_paper_id({"title": item.findtext("title", default=""), "source": feed.get("name", "rss")}),
                    "source": feed.get("name", "rss"),
                    "title": clean_whitespace(item.findtext("title", default="")),
                    "url": clean_whitespace(item.findtext("link", default="")),
                    "published_at": clean_whitespace(item.findtext("pubDate", default="")),
                }
                items.append(entry)
                count += 1
                if count >= max_items:
                    break
            logs.append(_log_source_run("social_signals", "ok", feed.get("name", "rss"), count))
        except Exception as exc:
            logs.append(_log_source_run("social_signals", "error", f"{feed.get('name', 'rss')}: {exc}", 0))
    return items, logs


def fetch_gmail_alerts(configs: dict) -> tuple[list[dict], list[dict]]:
    gmail_cfg = configs["sources"]["sources"].get("gmail_alerts", {})
    if not gmail_cfg.get("enabled", False):
        return [], [_log_source_run("gmail_alerts", "skipped", "Gmail alerts disabled", 0)]
    return [], [_log_source_run("gmail_alerts", "skipped", "Gmail integration is unavailable in local script mode", 0)]

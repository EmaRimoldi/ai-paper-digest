from __future__ import annotations

import hashlib
import html
import math
import re
from collections import Counter, defaultdict
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

import fitz
from pypdf import PdfReader

from .config import CATALOG_DIR, REPORTS_DIR, now_iso
from .storage import write_text

DEFAULT_SCHEMA = {
    "id": "",
    "source_ids": {
        "arxiv_id": "",
        "semantic_scholar_id": "",
        "openalex_id": "",
        "openreview_id": "",
        "doi": "",
    },
    "status": "new",
    "title": "",
    "authors": [],
    "institutions": [],
    "published_date": "",
    "updated_date": "",
    "source": "",
    "categories": [],
    "venue_or_status": "",
    "abstract": "",
    "url": "",
    "pdf_url": "",
    "local_pdf_path": "",
    "code_url": "",
    "project_page": "",
    "citation_count": None,
    "influential_citation_count": None,
    "topic_tags": [],
    "primary_topic": "",
    "secondary_topics": [],
    "fit_score": "Low",
    "priority": "Archive",
    "interestingness_score": 0.0,
    "novelty_signal": "unknown",
    "social_signal": "unknown",
    "evidence_type": "unknown",
    "summary_level": "metadata_only",
    "one_sentence_summary": "",
    "core_contribution": "",
    "method": "",
    "main_result_or_claim": "",
    "key_results": [],
    "limitations_or_caveats": "",
    "why_it_matters": "",
    "section_summaries": {},
    "public_note_path": "",
    "public_card_path": "",
    "safe_figure_paths": [],
    "discovered_at": "",
    "last_checked_at": "",
}

SECTION_PATTERNS = {
    "introduction": (
        r"(?im)^(?:§?\s*[ivxlcdm]+\.\s*introduction|§?\s*[0-9]+(?:\.[0-9]+)?\s*introduction|§?\s*introduction)\s*$",
    ),
    "method": (
        r"(?im)^(?:§?\s*[ivxlcdm]+\.\s*(?:method|methods|methodology|approach|framework)|§?\s*[0-9]+(?:\.[0-9]+)?\s*(?:method|methods|methodology|approach|framework)|§?\s*(?:method|methods|methodology|approach|framework))\s*$",
        r"(?im)^(?:§?\s*[ivxlcdm]+\.\s*(?:proposed method|proposed approach)|§?\s*[0-9]+(?:\.[0-9]+)?\s*(?:proposed method|proposed approach))\s*$",
    ),
    "results": (
        r"(?im)^(?:§?\s*[ivxlcdm]+\.\s*(?:experiments|experiment|results|evaluation|evaluations|experimental results)|§?\s*[0-9]+(?:\.[0-9]+)?\s*(?:experiments|experiment|results|evaluation|evaluations|experimental results)|§?\s*(?:experiments|experiment|results|evaluation|evaluations|experimental results))\s*$",
    ),
    "discussion": (
        r"(?im)^(?:§?\s*[ivxlcdm]+\.\s*(?:discussion|limitations|limitation|future work)|§?\s*[0-9]+(?:\.[0-9]+)?\s*(?:discussion|limitations|limitation|future work)|§?\s*(?:discussion|limitations|limitation|future work))\s*$",
    ),
    "conclusion": (
        r"(?im)^(?:§?\s*[ivxlcdm]+\.\s*(?:conclusion|conclusions)|§?\s*[0-9]+(?:\.[0-9]+)?\s*(?:conclusion|conclusions)|§?\s*(?:conclusion|conclusions))\s*$",
    ),
}

GENERIC_HEADING_PATTERN = re.compile(
    r"(?im)^(?:§?\s*[ivxlcdm]+\.\s*[a-z][^\n]{0,90}|§?\s*[0-9]+(?:\.[0-9]+)?\s*[a-z][^\n]{0,90}|"
    r"(?:introduction|background|preliminaries|method|methods|methodology|approach|framework|"
    r"experiments|experiment|results|evaluation|discussion|limitations|future work|conclusion|conclusions))\s*$"
)

TOPIC_KEYWORDS = {
    "foundation_models": [
        "llm",
        "language model",
        "foundation model",
        "transformer",
        "pretraining",
        "post-training",
        "reasoning",
        "multimodal",
        "test-time compute",
        "in-context",
        "scaling law",
    ],
    "agents": [
        "agent",
        "tool use",
        "computer use",
        "browser",
        "long-horizon",
        "multi-agent",
        "planner",
        "toolformer",
    ],
    "evaluation": [
        "benchmark",
        "evaluation",
        "verifier",
        "contamination",
        "judge",
        "human eval",
        "reproducibility",
        "measurement",
    ],
    "safety_alignment": [
        "alignment",
        "safety",
        "robustness",
        "jailbreak",
        "red teaming",
        "unlearning",
        "adversarial",
        "hazard",
    ],
    "theory_optimization": [
        "generalization",
        "optimization",
        "statistical learning",
        "learning theory",
        "pac-bayes",
        "sample complexity",
        "convex",
        "information theory",
    ],
    "reinforcement_learning": [
        "reinforcement learning",
        "offline rl",
        "policy optimization",
        "reward model",
        "bandit",
        "rlhf",
    ],
    "neuroai": [
        "neuroai",
        "computational neuroscience",
        "neural coding",
        "brain",
        "cognitive",
        "biologically inspired",
    ],
    "automated_research": [
        "ai scientist",
        "automated research",
        "literature review",
        "research agent",
        "scientific discovery",
        "paper writing",
    ],
    "interpretability": [
        "mechanistic interpretability",
        "interpretability",
        "circuit",
        "representation analysis",
        "feature visualization",
    ],
    "benchmarks": [
        "benchmark design",
        "verifier design",
        "benchmark methodology",
        "reproducibility",
        "leaderboard",
    ],
}


def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def strip_tags(text: str) -> str:
    return clean_whitespace(html.unescape(re.sub(r"<[^>]+>", " ", text or "")))


def slugify(text: str, limit: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", clean_whitespace(text).lower()).strip("-")
    if not slug:
        slug = "untitled-paper"
    return slug[:limit].rstrip("-")


def normalize_title(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_whitespace(text).lower())


def stable_paper_id(paper: dict) -> str:
    ids = paper.get("source_ids", {})
    for key in ("arxiv_id", "doi", "semantic_scholar_id", "openalex_id", "openreview_id"):
        value = clean_whitespace(str(ids.get(key, "")))
        if value:
            return value
    basis = f"{normalize_title(paper.get('title', ''))}|{paper.get('source', '')}"
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]


def first_author_name(paper: dict) -> str:
    authors = paper.get("authors", [])
    return clean_whitespace(authors[0]) if authors else ""


def ensure_schema(paper: dict) -> dict:
    normalized = {**DEFAULT_SCHEMA, **paper}
    normalized["source_ids"] = {**DEFAULT_SCHEMA["source_ids"], **paper.get("source_ids", {})}
    normalized["title"] = clean_whitespace(normalized["title"])
    normalized["abstract"] = clean_whitespace(normalized["abstract"])
    normalized["authors"] = [clean_whitespace(author) for author in normalized.get("authors", []) if clean_whitespace(author)]
    normalized["categories"] = [clean_whitespace(category) for category in normalized.get("categories", []) if clean_whitespace(category)]
    normalized["institutions"] = [
        clean_whitespace(inst) for inst in normalized.get("institutions", []) if clean_whitespace(inst)
    ]
    normalized["topic_tags"] = [
        clean_whitespace(tag) for tag in normalized.get("topic_tags", []) if clean_whitespace(tag)
    ]
    normalized["secondary_topics"] = [
        clean_whitespace(tag) for tag in normalized.get("secondary_topics", []) if clean_whitespace(tag)
    ]
    normalized["key_results"] = [clean_whitespace(item) for item in normalized.get("key_results", []) if clean_whitespace(item)]
    normalized["section_summaries"] = {
        clean_whitespace(str(key)): clean_whitespace(str(value))
        for key, value in (normalized.get("section_summaries") or {}).items()
        if clean_whitespace(str(key)) and clean_whitespace(str(value))
    }
    normalized["id"] = normalized["id"] or stable_paper_id(normalized)
    normalized["last_checked_at"] = normalized.get("last_checked_at") or now_iso()
    if not normalized.get("discovered_at"):
        normalized["discovered_at"] = now_iso()
    return normalized


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def deduplicate_papers(candidates: list[dict], existing: list[dict], threshold: float) -> tuple[list[dict], list[dict]]:
    unique: list[dict] = []
    duplicates: list[dict] = []
    existing_pool = [ensure_schema(item) for item in existing]
    seen_ids = {
        stable_paper_id(item)
        for item in existing_pool
        if item.get("title") or any(item.get("source_ids", {}).values())
    }
    seen_titles = [item.get("title", "") for item in existing_pool if item.get("title")]
    seen_exact_titles = {normalize_title(title) for title in seen_titles}
    for raw_candidate in candidates:
        candidate = ensure_schema(raw_candidate)
        candidate_id = stable_paper_id(candidate)
        normalized_title = normalize_title(candidate.get("title", ""))
        is_duplicate = candidate_id in seen_ids or normalized_title in seen_exact_titles
        if not is_duplicate and normalized_title:
            is_duplicate = any(similarity(candidate["title"], title) >= threshold for title in seen_titles)
        if is_duplicate:
            candidate["status"] = "duplicate"
            duplicates.append(candidate)
            continue
        seen_ids.add(candidate_id)
        if normalized_title:
            seen_exact_titles.add(normalized_title)
            seen_titles.append(candidate["title"])
        unique.append(candidate)
    return unique, duplicates


def topic_scores(text: str) -> dict[str, float]:
    lowered = text.lower()
    scores: dict[str, float] = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = 0.0
        for keyword in keywords:
            if keyword in lowered:
                score += 1.0
        scores[topic] = score
    return scores


def assign_topics_to_paper(paper: dict, taxonomy: dict) -> dict:
    text = " ".join(
        [
            paper.get("title", ""),
            paper.get("abstract", ""),
            " ".join(paper.get("categories", [])),
        ]
    )
    scores = topic_scores(text)
    ranked = [topic for topic, score in sorted(scores.items(), key=lambda item: item[1], reverse=True) if score > 0]
    topics = taxonomy.get("topics", {})
    primary = ranked[0] if ranked else "foundation_models"
    if primary not in topics:
        primary = next(iter(topics), "foundation_models")
    secondary = [topic for topic in ranked[1:3] if topic != primary and topic in topics]
    paper["primary_topic"] = primary
    paper["secondary_topics"] = secondary
    topic_tags = set(paper.get("topic_tags", []))
    topic_tags.add(primary)
    topic_tags.update(secondary)
    paper["topic_tags"] = sorted(topic_tags)
    return paper


def detect_evidence_type(paper: dict) -> str:
    text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
    if any(keyword in text for keyword in ("theorem", "generalization bound", "sample complexity", "proof")):
        return "theory"
    if any(keyword in text for keyword in ("benchmark", "evaluation suite", "leaderboard")):
        return "benchmark"
    if any(keyword in text for keyword in ("survey", "overview", "taxonomy")):
        return "survey"
    if any(keyword in text for keyword in ("system", "infrastructure", "toolchain")):
        return "system"
    if any(keyword in text for keyword in ("position paper", "perspective")):
        return "position"
    if any(keyword in text for keyword in ("experiment", "empirical", "ablations")):
        return "experiments"
    if paper.get("abstract"):
        return "mixed"
    return "unknown"


def _count_keywords(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lowered)


def _fit_numeric(paper: dict, profile: dict, queries: dict) -> float:
    text = " ".join(
        [
            paper.get("title", ""),
            paper.get("abstract", ""),
            " ".join(paper.get("categories", [])),
            paper.get("primary_topic", ""),
        ]
    ).lower()
    high_priority = profile.get("research_interests", {}).get("high_priority", [])
    medium_priority = profile.get("research_interests", {}).get("medium_priority", [])
    score = 0.0
    score += sum(1.2 for term in high_priority if term.lower() in text)
    score += sum(0.6 for term in medium_priority if term.lower() in text)
    for keywords in queries.get("keyword_groups", {}).values():
        score += min(_count_keywords(text, keywords), 3) * 0.5
    score += topic_scores(text).get(paper.get("primary_topic", ""), 0.0) * 0.4
    return score


def _recency_score(paper: dict, run_date: date) -> float:
    raw_date = paper.get("published_date") or paper.get("updated_date")
    if not raw_date:
        return 0.3
    try:
        published = date.fromisoformat(raw_date[:10])
    except ValueError:
        return 0.3
    days_old = max((run_date - published).days, 0)
    return max(0.0, 1.2 - min(days_old, 14) * 0.08)


def _abstract_quality(paper: dict) -> float:
    words = clean_whitespace(paper.get("abstract", "")).split()
    if len(words) >= 140:
        return 1.0
    if len(words) >= 80:
        return 0.7
    if len(words) >= 30:
        return 0.4
    return 0.1


def _technical_depth(paper: dict) -> float:
    text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
    signals = [
        "theorem",
        "proof",
        "optimization",
        "sample complexity",
        "scaling law",
        "benchmark",
        "mechanistic",
        "ablation",
        "policy",
        "representation",
        "verification",
    ]
    return min(sum(1 for signal in signals if signal in text) * 0.25, 1.8)


def _novelty_signal(paper: dict) -> tuple[str, float]:
    text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
    score = 0.0
    for signal in ("first", "new", "novel", "introduce", "propose", "discover", "unify"):
        if signal in text:
            score += 0.25
    if score >= 1.0:
        return "high", 1.0
    if score >= 0.5:
        return "medium", 0.6
    if score > 0.0:
        return "low", 0.3
    return "unknown", 0.1


def _social_numeric(value: str) -> float:
    return {"high": 1.0, "medium": 0.6, "low": 0.3, "unknown": 0.0}.get(value, 0.0)


def _importance_score(paper: dict) -> float:
    citation_count = paper.get("citation_count") or 0
    influential = paper.get("influential_citation_count") or 0
    citation_term = min(math.log10(citation_count + 1) / 2.0, 1.0)
    influential_term = min(math.log10(influential + 1) / 2.0, 1.0)
    return max(citation_term, influential_term * 1.1)


def determine_priority(score: float, scoring: dict) -> str:
    thresholds = scoring.get("priority_thresholds", {})
    if score >= thresholds.get("must_read", 7.2):
        return "Must read"
    if score >= thresholds.get("skim", 4.4):
        return "Skim"
    return "Archive"


def determine_fit_label(score: float, scoring: dict) -> str:
    thresholds = scoring.get("fit_thresholds", {})
    if score >= thresholds.get("high", 6.0):
        return "High"
    if score >= thresholds.get("medium", 3.5):
        return "Medium"
    return "Low"


def rank_papers(
    papers: list[dict],
    profile: dict,
    queries: dict,
    scoring: dict,
    taxonomy: dict,
    run_date: date,
) -> list[dict]:
    weights = scoring.get("weights", {})
    for paper in papers:
        assign_topics_to_paper(paper, taxonomy)
        fit_score_numeric = _fit_numeric(paper, profile, queries)
        novelty_label, novelty_numeric = _novelty_signal(paper)
        paper["novelty_signal"] = novelty_label
        paper["evidence_type"] = detect_evidence_type(paper)
        paper["fit_score"] = determine_fit_label(fit_score_numeric, scoring)
        paper["interestingness_score"] = round(
            fit_score_numeric * weights.get("topic_fit", 3.0) / 3.0
            + _technical_depth(paper) * weights.get("technical_depth", 1.7)
            + novelty_numeric * weights.get("novelty", 1.5)
            + _importance_score(paper) * weights.get("likely_importance", 1.3)
            + _abstract_quality(paper) * weights.get("abstract_quality", 1.0)
            + _social_numeric(paper.get("social_signal", "unknown")) * weights.get("social_signal", 0.8)
            + (0.8 if paper.get("code_url") or paper.get("project_page") else 0.0) * weights.get("code_or_project", 0.5)
            + (0.8 if paper.get("venue_or_status") else 0.0) * weights.get("venue_signal", 0.5)
            + min(topic_scores((paper.get("title", "") + " " + paper.get("abstract", "")).lower()).values() or [0.0], default=0.0)
            * 0.0
            + _recency_score(paper, run_date) * weights.get("recency", 0.7),
            3,
        )
        paper["priority"] = determine_priority(paper["interestingness_score"], scoring)
    ranked = sorted(
        [ensure_schema(paper) for paper in papers],
        key=lambda item: (
            item.get("priority") != "Must read",
            -float(item.get("interestingness_score", 0.0)),
            item.get("title", ""),
        ),
    )
    max_per_topic = scoring.get("diversity", {}).get("max_same_primary_topic_in_top10", 3)
    selected: list[dict] = []
    topic_counts: Counter[str] = Counter()
    for paper in ranked:
        primary = paper.get("primary_topic", "")
        if len(selected) < 10 and topic_counts[primary] >= max_per_topic and paper.get("priority") == "Must read":
            continue
        if len(selected) < 10 and topic_counts[primary] >= max_per_topic and paper.get("priority") != "Must read":
            continue
        selected.append(paper)
        topic_counts[primary] += 1
    if len(selected) < 10:
        already = {paper["id"] for paper in selected}
        for paper in ranked:
            if paper["id"] in already:
                continue
            selected.append(paper)
            if len(selected) >= 10:
                break
    selected_ids = {paper["id"] for paper in selected[:10]}
    for paper in ranked:
        paper["status"] = "active" if paper["id"] in selected_ids else paper.get("status", "new")
    return ranked


def split_sentences(text: str) -> list[str]:
    cleaned = clean_whitespace(text)
    if not cleaned:
        return []
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", cleaned)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def truncate(text: str, limit: int) -> str:
    cleaned = clean_whitespace(text)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _pdf_path(paper: dict) -> Path | None:
    local_path = clean_whitespace(paper.get("local_pdf_path", ""))
    if not local_path:
        return None
    path = Path(local_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path
    return path if path.exists() else None


def extract_pdf_raw_text(paper: dict, max_pages: int = 8) -> str:
    pdf_path = _pdf_path(paper)
    if not pdf_path:
        return ""
    try:
        document = fitz.open(str(pdf_path))
        try:
            text_parts = []
            for page in document[:max_pages]:
                text = page.get_text() or ""
                if text:
                    text_parts.append(text)
            if text_parts:
                return "\n\n---PAGE---\n\n".join(text_parts)
        finally:
            document.close()
    except Exception:
        pass
    try:
        reader = PdfReader(str(pdf_path))
        text_parts = []
        for page in reader.pages[:max_pages]:
            text = page.extract_text() or ""
            if text:
                text_parts.append(text)
        return "\n\n---PAGE---\n\n".join(text_parts)
    except Exception:
        return ""


def extract_pdf_text(paper: dict, max_pages: int = 8) -> str:
    return _clean_pdf_text(extract_pdf_raw_text(paper, max_pages=max_pages))


def _clean_pdf_text(text: str) -> str:
    cleaned = text or ""
    cleaned = cleaned.replace("§", " ")
    cleaned = re.sub(r"([A-Za-z])-\s*\n\s*([A-Za-z])", r"\1\2", cleaned)
    cleaned = re.sub(r"([A-Za-z])-\s+([A-Za-z])", r"\1\2", cleaned)
    cleaned = re.sub(r"arXiv:[^\n ]+", " ", cleaned)
    cleaned = re.sub(r"\bPreprint\b", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"Disclaimer:[^.]+(?:\.)?", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"https?://\S+", " ", cleaned)
    cleaned = re.sub(r"\b(?:Introduction|Contents|Table of Contents)\b", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"---PAGE---", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return clean_whitespace(cleaned)


def _normalize_pdf_for_sections(text: str) -> str:
    normalized = text or ""
    normalized = normalized.replace("\r", "\n")
    normalized = re.sub(r"([A-Za-z])-\s*\n\s*([A-Za-z])", r"\1\2", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = normalized.replace("§", "")
    lines = []
    for raw_line in normalized.splitlines():
        line = clean_whitespace(raw_line)
        if not line:
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if line == "---PAGE---":
            continue
        lines.append(line)
    return "\n".join(lines)


def _find_first_match(text: str, patterns: tuple[str, ...]) -> re.Match[str] | None:
    matches = [re.search(pattern, text) for pattern in patterns]
    valid = [match for match in matches if match]
    if not valid:
        return None
    return min(valid, key=lambda match: match.start())


def _next_heading_start(text: str, after: int) -> int:
    match = GENERIC_HEADING_PATTERN.search(text, after)
    return match.start() if match else len(text)


def _section_block(text: str, section_name: str) -> str:
    patterns = SECTION_PATTERNS.get(section_name, ())
    start_match = _find_first_match(text, patterns)
    if not start_match:
        return ""
    start = start_match.end()
    end = _next_heading_start(text, start)
    return clean_whitespace(text[start:end])


def _front_matter_candidate(text: str) -> str:
    intro_match = _find_first_match(text, SECTION_PATTERNS["introduction"])
    front = text[: intro_match.start()] if intro_match else text[:4000]
    lines = []
    for line in front.splitlines():
        lowered = line.lower()
        if any(
            token in lowered
            for token in (
                "homepage:",
                "github repo:",
                "contact:",
                "joint first author",
                "correspondence author",
                "university",
                "institute",
                "school of",
                "department of",
                "date:",
                "preprint",
            )
        ):
            continue
        lines.append(line)
    return clean_whitespace(" ".join(lines))


def extract_pdf_sections(paper: dict, max_pages: int = 8) -> dict[str, str]:
    raw_text = extract_pdf_raw_text(paper, max_pages=max_pages)
    if not raw_text:
        return {}
    section_text = _normalize_pdf_for_sections(raw_text)
    sections = {
        "front_matter": _front_matter_candidate(section_text),
        "introduction": _section_block(section_text, "introduction"),
        "method": _section_block(section_text, "method"),
        "results": _section_block(section_text, "results"),
        "discussion": _section_block(section_text, "discussion"),
        "conclusion": _section_block(section_text, "conclusion"),
    }
    sections["abstract"] = clean_whitespace(paper.get("abstract", "")) or sections["front_matter"]
    return {key: value for key, value in sections.items() if clean_whitespace(value)}


def _dedupe_sentences(sentences: list[str], limit: int = 6) -> list[str]:
    unique: list[str] = []
    seen_normalized: set[str] = set()
    for sentence in sentences:
        normalized = normalize_title(sentence)
        if not normalized or normalized in seen_normalized:
            continue
        seen_normalized.add(normalized)
        unique.append(sentence)
        if len(unique) >= limit:
            break
    return unique


def _pick_sentences(sentences: list[str], keywords: tuple[str, ...], limit: int = 3) -> list[str]:
    chosen = [
        sentence
        for sentence in sentences
        if any(keyword in sentence.lower() for keyword in keywords)
    ]
    return _dedupe_sentences(chosen, limit=limit)


def _fallback_slice(sentences: list[str], start: int, stop: int, limit: int = 3) -> list[str]:
    return _dedupe_sentences(sentences[start:stop], limit=limit)


def _is_useful_sentence(sentence: str) -> bool:
    cleaned = clean_whitespace(sentence)
    lowered = cleaned.lower()
    if len(cleaned) < 50:
        return False
    blocked_terms = (
        "arxiv:",
        "preprint",
        "table of contents",
        "contents",
        "homepage:",
        "github repo:",
        "contact:",
        "university of",
        "institute of",
        "school of",
        "department of",
        "joint first author",
        "correspondence author",
    )
    if any(term in lowered for term in blocked_terms):
        return False
    if re.search(r"\b\d+(?:\.\d+){1,}\b", cleaned):
        return False
    if re.search(r"\b(?:introduction|preliminaries|motivation|experiments|conclusion)\b.*\b(?:\d+(?:\.\d+)?\b)", lowered):
        return False
    if re.fullmatch(r"[\d.\s]+", cleaned):
        return False
    if cleaned.count("§") >= 1:
        return False
    if len(re.findall(r"\b[A-Z][a-z]+\b", cleaned)) >= 8 and cleaned.count(",") >= 4:
        return False
    if re.search(r"\b(?:fig(?:ure)?|table)\s+\d+\b", lowered):
        return False
    return True


def _distinct_from(sentence: str, others: list[str], threshold: float = 0.84) -> bool:
    candidate = normalize_title(sentence)
    if not candidate:
        return False
    for other in others:
        if not other:
            continue
        if similarity(sentence, other) >= threshold:
            return False
    return True


def _derive_contribution_sentences(sentences: list[str]) -> list[str]:
    chosen = _pick_sentences(
        sentences,
        (
            "we propose",
            "we present",
            "we introduce",
            "this paper",
            "this work",
            "our framework",
            "our method",
            "we study",
            "we analyze",
            "we synthesize",
        ),
        limit=3,
    )
    return chosen or _fallback_slice(sentences, 0, 3, limit=3)


def _prefer_quantitative(sentences: list[str]) -> list[str]:
    quantitative = [
        sentence
        for sentence in sentences
        if re.search(r"\b\d+(?:\.\d+)?\s*(?:%|x|ms|points|tokens|examples|benchmarks?)\b", sentence.lower())
    ]
    return quantitative or sentences


def _derive_method_sentence(primary_sentences: list[str], backup_sentences: list[str], avoid: list[str]) -> str:
    for candidate_pool in (primary_sentences, backup_sentences):
        chosen = _pick_sentences(
            candidate_pool,
            (
                "method",
                "approach",
                "framework",
                "architecture",
                "algorithm",
                "pipeline",
                "using ",
                "through ",
                "via ",
                "we synthesize",
                "we formulate",
                "we cast",
                "we train",
                "we optimize",
                "we integrate",
                "we embed",
                "we decompose",
                "by aligning",
                "taxonomy",
            ),
            limit=6,
        )
        for item in chosen:
            if _distinct_from(item, avoid):
                return item
    return "unknown"


def _derive_result_sentences(primary_sentences: list[str], backup_sentences: list[str], avoid: list[str]) -> list[str]:
    for candidate_pool in (primary_sentences, backup_sentences):
        chosen = _pick_sentences(
            candidate_pool,
            (
                "results show",
                "we show",
                "we demonstrate",
                "outperform",
                "achieve",
                "improve",
                "reduce",
                "increase",
                "benchmark",
                "experiments",
                "evaluation",
                "we analyze",
                "we summarize",
                "we find",
            ),
            limit=6,
        )
        distinct = [item for item in _prefer_quantitative(chosen) if _distinct_from(item, avoid)]
        if distinct:
            return distinct[:3]
    fallback = _fallback_slice(primary_sentences or backup_sentences, 1, 5, limit=4)
    return [item for item in fallback if _distinct_from(item, avoid)][:3]


def _derive_caveat_sentence(sentences: list[str], used_pdf: bool) -> str:
    caveat = _pick_sentences(
        sentences,
        (
            "limitation",
            "limitations",
            "however",
            "future work",
            "challenge",
            "fails",
            "failure",
        ),
        limit=1,
    )
    if caveat:
        return caveat[0]
    if used_pdf:
        return "Fast note from local PDF text. Verify claims and limitations directly in the paper."
    return "Summary based on abstract/metadata only."


def _distinct_sentence_block(sentences: list[str], limit: int = 2, avoid: list[str] | None = None) -> list[str]:
    chosen: list[str] = []
    blocked = avoid or []
    for sentence in sentences:
        if _distinct_from(sentence, chosen + blocked, threshold=0.9):
            chosen.append(sentence)
        if len(chosen) >= limit:
            break
    return chosen


def _summarize_section(
    primary_sentences: list[str],
    backup_sentences: list[str],
    keywords: tuple[str, ...] = (),
    limit: int = 2,
    avoid: list[str] | None = None,
    fallback: str = "",
) -> str:
    for candidate_pool in (primary_sentences, backup_sentences):
        if not candidate_pool:
            continue
        matching = [
            sentence
            for sentence in candidate_pool
            if not keywords or any(keyword in sentence.lower() for keyword in keywords)
        ]
        chosen = _distinct_sentence_block(matching or candidate_pool, limit=limit, avoid=avoid)
        if chosen:
            return clean_whitespace(" ".join(chosen))
    return clean_whitespace(fallback)


def _derive_section_summaries(
    abstract_sentences: list[str],
    introduction_sentences: list[str],
    method_sentences: list[str],
    result_sentences: list[str],
    discussion_sentences: list[str],
    conclusion_sentences: list[str],
    pdf_sentences: list[str],
    paper: dict,
) -> dict[str, str]:
    abstract_summary = _summarize_section(
        abstract_sentences,
        pdf_sentences,
        limit=2,
        fallback=paper.get("one_sentence_summary", ""),
    )
    introduction_summary = _summarize_section(
        introduction_sentences,
        abstract_sentences or pdf_sentences,
        keywords=(
            "we study",
            "we analyze",
            "we consider",
            "problem",
            "challenge",
            "goal",
            "motivation",
            "urgent",
            "important",
        ),
        limit=2,
        fallback=paper.get("core_contribution", ""),
    )
    method_summary = _summarize_section(
        method_sentences,
        pdf_sentences,
        keywords=(
            "method",
            "approach",
            "framework",
            "algorithm",
            "architecture",
            "pipeline",
            "using ",
            "through ",
            "via ",
            "we formulate",
            "we cast",
            "we train",
            "we optimize",
            "taxonomy",
        ),
        limit=2,
        fallback=paper.get("method", ""),
    )
    results_summary = _summarize_section(
        result_sentences,
        pdf_sentences,
        keywords=(
            "results show",
            "we show",
            "we demonstrate",
            "outperform",
            "achieve",
            "improve",
            "reduce",
            "increase",
            "benchmark",
            "evaluation",
            "we find",
        ),
        limit=3,
        fallback=paper.get("main_result_or_claim", ""),
    )
    limitations_summary = _summarize_section(
        discussion_sentences,
        conclusion_sentences or pdf_sentences,
        keywords=(
            "limitation",
            "limitations",
            "however",
            "future work",
            "challenge",
            "fails",
            "failure",
            "trade-off",
            "tradeoff",
        ),
        limit=2,
        fallback=paper.get("limitations_or_caveats", ""),
    )
    conclusion_summary = _summarize_section(
        conclusion_sentences,
        discussion_sentences or pdf_sentences,
        keywords=(
            "in conclusion",
            "to conclude",
            "overall",
            "we conclude",
            "we find",
            "this work",
            "this paper",
        ),
        limit=2,
        fallback=paper.get("why_it_matters", ""),
    )
    return {
        "abstract": abstract_summary,
        "introduction": introduction_summary,
        "method": method_summary,
        "results": results_summary,
        "limitations": limitations_summary,
        "conclusion": conclusion_summary,
    }


def summarize_paper(paper: dict) -> dict:
    paper = ensure_schema(paper)
    pdf_sections = extract_pdf_sections(paper)
    abstract_sentences = [sentence for sentence in split_sentences(pdf_sections.get("abstract", "")) if _is_useful_sentence(sentence)]
    introduction_sentences = [
        sentence for sentence in split_sentences(pdf_sections.get("introduction", "")) if _is_useful_sentence(sentence)
    ]
    method_sentences = [sentence for sentence in split_sentences(pdf_sections.get("method", "")) if _is_useful_sentence(sentence)]
    result_sentences_pool = [sentence for sentence in split_sentences(pdf_sections.get("results", "")) if _is_useful_sentence(sentence)]
    discussion_sentences = [
        sentence
        for sentence in split_sentences(pdf_sections.get("discussion", ""))
        if _is_useful_sentence(sentence)
    ]
    conclusion_sentences = [
        sentence
        for sentence in split_sentences(pdf_sections.get("conclusion", ""))
        if _is_useful_sentence(sentence)
    ]
    pdf_text = extract_pdf_text(paper)
    pdf_sentences = [sentence for sentence in split_sentences(pdf_text) if _is_useful_sentence(sentence)]
    used_pdf = any((introduction_sentences, method_sentences, result_sentences_pool, discussion_sentences, conclusion_sentences))
    primary_sentences = abstract_sentences or introduction_sentences or pdf_sentences
    contribution_source = introduction_sentences or abstract_sentences or pdf_sentences
    method_source = method_sentences or pdf_sentences
    result_source = result_sentences_pool or pdf_sentences
    discussion_source = discussion_sentences or conclusion_sentences or pdf_sentences
    sentences = primary_sentences or pdf_sentences
    if used_pdf or pdf_sentences:
        paper["summary_level"] = "pdf_summary"
    elif paper.get("abstract"):
        paper["summary_level"] = "abstract_summary"
    else:
        paper["summary_level"] = "metadata_only"
    if sentences:
        contribution_sentences = _derive_contribution_sentences(contribution_source)
        first = contribution_sentences[0] if contribution_sentences else primary_sentences[0]
        method_sentence = _derive_method_sentence(method_source, pdf_sentences, avoid=contribution_sentences)
        result_sentences = _derive_result_sentences(
            result_source,
            pdf_sentences,
            avoid=contribution_sentences + [method_sentence],
        )
        result_sentence = result_sentences[0] if result_sentences else "unknown"
        paper["one_sentence_summary"] = first
        paper["core_contribution"] = contribution_sentences[0] if contribution_sentences else first
        paper["method"] = method_sentence
        paper["main_result_or_claim"] = result_sentence
        paper["key_results"] = result_sentences[:3] or [first]
        paper["limitations_or_caveats"] = _derive_caveat_sentence(discussion_source, used_pdf=used_pdf)
    else:
        paper["one_sentence_summary"] = (
            f"{paper.get('title', 'This paper')} appears relevant, but the summary is based on metadata only."
        )
        paper["core_contribution"] = "Summary based on abstract/metadata only."
        paper["method"] = "unknown"
        paper["main_result_or_claim"] = "unknown"
        paper["key_results"] = ["Summary based on abstract/metadata only."]
        paper["limitations_or_caveats"] = "Summary based on abstract/metadata only."
    topic_title = paper.get("primary_topic", "").replace("_", " ")
    paper["why_it_matters"] = (
        f"It looks relevant to {topic_title or 'current AI research'} and is a plausible candidate for a first-pass read."
    )
    paper["section_summaries"] = _derive_section_summaries(
        abstract_sentences=abstract_sentences,
        introduction_sentences=introduction_sentences,
        method_sentences=method_sentences,
        result_sentences=result_sentences_pool,
        discussion_sentences=discussion_sentences,
        conclusion_sentences=conclusion_sentences,
        pdf_sentences=pdf_sentences,
        paper=paper,
    )
    return paper


def build_author_index(papers: list[dict]) -> list[dict]:
    counts: dict[str, dict] = {}
    for paper in papers:
        for author in paper.get("authors", []):
            entry = counts.setdefault(author, {"author": author, "paper_count": 0, "latest_paper": ""})
            entry["paper_count"] += 1
            entry["latest_paper"] = paper.get("title", entry["latest_paper"])
    return sorted(counts.values(), key=lambda item: (-item["paper_count"], item["author"]))


def build_venue_index(papers: list[dict]) -> list[dict]:
    counts: dict[str, dict] = {}
    for paper in papers:
        venue = clean_whitespace(paper.get("venue_or_status", "")) or "unknown"
        entry = counts.setdefault(venue, {"venue": venue, "paper_count": 0})
        entry["paper_count"] += 1
    return sorted(counts.values(), key=lambda item: (-item["paper_count"], item["venue"]))


def update_taxonomy_assignments(
    selected_papers: list[dict],
    taxonomy: dict,
    run_date: date,
) -> tuple[list[dict], list[dict], str | None]:
    assignments: list[dict] = []
    misc_like = 0
    for paper in selected_papers:
        assign_topics_to_paper(paper, taxonomy)
        assignment = {
            "paper_id": paper["id"],
            "title": paper["title"],
            "primary_topic": paper["primary_topic"],
            "secondary_topics": paper.get("secondary_topics", []),
            "assigned_at": now_iso(),
        }
        assignments.append(assignment)
        if paper["primary_topic"] not in taxonomy.get("topics", {}):
            misc_like += 1
    proposal_path = None
    if misc_like >= 5:
        proposal_path = REPORTS_DIR / "taxonomy_proposals" / f"{run_date.isoformat()}.md"
        write_text(
            proposal_path,
            "\n".join(
                [
                    f"# Taxonomy Proposal — {run_date.isoformat()}",
                    "",
                    "A large number of selected papers did not map cleanly to the current taxonomy.",
                    "Review recent notes and consider adding a new subtopic or topic split.",
                ]
            ),
        )
    return selected_papers, assignments, str(proposal_path) if proposal_path else None


def note_path_for_paper(run_date: date, paper: dict) -> Path:
    return CATALOG_DIR / "papers" / run_date.isoformat() / f"{slugify(paper['title'])}.md"


def topic_counts(papers: list[dict]) -> dict[str, int]:
    counts = Counter(paper.get("primary_topic", "unknown") for paper in papers if paper.get("primary_topic"))
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def top_topic_rows(papers: list[dict], topic_slug: str, limit: int = 10) -> list[dict]:
    filtered = [paper for paper in papers if paper.get("primary_topic") == topic_slug]
    return sorted(filtered, key=lambda item: item.get("published_date", ""), reverse=True)[:limit]


def grouped_by_topic(papers: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for paper in papers:
        grouped[paper.get("primary_topic", "foundation_models")].append(paper)
    return grouped

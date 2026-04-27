from __future__ import annotations

import hashlib
import html
import math
import re
from collections import Counter, defaultdict
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

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
    "public_note_path": "",
    "public_card_path": "",
    "safe_figure_paths": [],
    "discovered_at": "",
    "last_checked_at": "",
}

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


def summarize_paper(paper: dict) -> dict:
    paper = ensure_schema(paper)
    sentences = split_sentences(paper.get("abstract", ""))
    if paper.get("abstract"):
        paper["summary_level"] = "abstract_summary"
    else:
        paper["summary_level"] = "metadata_only"
    if sentences:
        first = truncate(sentences[0], 180)
        method_sentence = next(
            (sentence for sentence in sentences if any(term in sentence.lower() for term in ("method", "approach", "framework", "model"))),
            sentences[min(1, len(sentences) - 1)],
        )
        result_sentence = next(
            (
                sentence
                for sentence in sentences
                if any(term in sentence.lower() for term in ("result", "achieve", "outperform", "show", "demonstrate"))
            ),
            sentences[min(2, len(sentences) - 1)],
        )
        paper["one_sentence_summary"] = first
        paper["core_contribution"] = truncate(first, 220)
        paper["method"] = truncate(method_sentence, 220)
        paper["main_result_or_claim"] = truncate(result_sentence, 220)
        paper["key_results"] = [truncate(sentence, 160) for sentence in sentences[1:4]] or [truncate(first, 160)]
    else:
        paper["one_sentence_summary"] = truncate(
            f"{paper.get('title', 'This paper')} appears relevant, but the summary is based on metadata only.",
            180,
        )
        paper["core_contribution"] = "Summary based on abstract/metadata only."
        paper["method"] = "unknown"
        paper["main_result_or_claim"] = "unknown"
        paper["key_results"] = ["Summary based on abstract/metadata only."]
    if paper.get("local_pdf_path"):
        paper["limitations_or_caveats"] = paper.get("limitations_or_caveats") or "Fast note. Verify claims directly in the paper before relying on them."
    else:
        paper["limitations_or_caveats"] = "Summary based on abstract/metadata only."
    topic_title = paper.get("primary_topic", "").replace("_", " ")
    paper["why_it_matters"] = truncate(
        f"It looks relevant to {topic_title or 'current AI research'} and is a plausible candidate for a first-pass read.",
        180,
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


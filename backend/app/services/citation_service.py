"""Metadata-grounded retrieval used by the assistant.

The retriever scores investigation metadata fields with inverse document
frequency weighting, returns evidence snippets, and never invents facts.
"""

from __future__ import annotations

import math
import re
from typing import Any

from app.data_pipeline.metadata_repository import store
from app.utils.formatting import human_bytes, normalize_space

STOPWORDS = {
    "a", "about", "above", "after", "again", "all", "also", "am", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "could", "did", "do",
    "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "itself", "just", "me", "more", "most", "my", "myself",
    "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or",
    "other", "our", "ours", "ourselves", "out", "over", "own", "same",
    "she", "should", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "will", "with", "would", "you", "your", "yours", "yourself",
    "yourselves", "tell", "show", "list", "find", "give", "explain",
    "experiment", "experiments", "investigation", "investigations", "research",
    "study", "studies", "studied", "data", "nasa", "psi", "which", "used",
    "using", "use", "between", "difference", "differences", "available",
}


def _tokenize(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9][a-z0-9\-]{1,}", (text or "").lower())
        if token not in STOPWORDS and len(token) >= 3
    ]


def _field_text(record: dict[str, Any]) -> dict[str, str]:
    description = record.get("description") or {}
    fields = {
        "title": record.get("title") or "",
        "acronym": record.get("acronym") or "",
        "keywords": " ".join(record.get("keywords") or []),
        "sub_research_area": record.get("sub_research_area") or "",
        "research_area": record.get("research_area") or "",
        "flight_platform": record.get("flight_platform") or "",
        "proposal_title": record.get("proposal_title") or "",
        "objectives": description.get("objectives") or "",
        "approach": description.get("approach") or "",
        "hypothesis": description.get("hypothesis") or "",
        "research_impacts": description.get("research_impacts") or "",
    }
    hardware = record.get("experiment_hardware") or {}
    fields["experiment_hardware"] = hardware.get("name") or ""

    storage_row = store.get_storage_row(record["investigation_id"])
    if storage_row:
        file_counts = storage_row.get("file_counts") or {}
        storage = storage_row.get("storage") or {}
        formats = ", ".join(
            f"{extension} ({count})"
            for extension, count in list((storage_row.get("format_distribution") or {}).items())[:8]
        )
        fields["file_inventory"] = (
            f"{file_counts.get('total_discovered', 0)} files; "
            f"remote inventory {storage.get('remote_inventory_size_human', 'unknown')}; "
            f"formats: {formats}; "
            f"{file_counts.get('pending_download', 0)} files within the 100 MiB limit, "
            f"{file_counts.get('over_limit', 0)} over limit; downloaded locally: 0."
        )
        datasets = store.get_datasets(record["investigation_id"])
        if datasets:
            categories = sorted({item.get("top_level_category") or "" for item in datasets})
            fields["dataset_groups"] = (
                f"{len(datasets)} derived file groups across categories: "
                + ", ".join(category for category in categories if category)
            )
    return fields


FIELD_WEIGHTS = {
    "title": 4.0,
    "acronym": 3.2,
    "keywords": 2.2,
    "sub_research_area": 1.9,
    "proposal_title": 1.7,
    "experiment_hardware": 1.6,
    "file_inventory": 1.6,
    "objectives": 1.5,
    "approach": 1.5,
    "hypothesis": 1.4,
    "research_impacts": 1.2,
    "flight_platform": 1.2,
    "dataset_groups": 1.1,
    "research_area": 0.9,
}

FIELD_LABELS = {
    "title": "Title",
    "acronym": "Acronym",
    "keywords": "Keywords",
    "sub_research_area": "Sub-research area",
    "proposal_title": "Proposal title",
    "experiment_hardware": "Experiment hardware",
    "file_inventory": "File inventory",
    "objectives": "Objectives",
    "approach": "Approach",
    "hypothesis": "Hypothesis",
    "research_impacts": "Research impacts",
    "flight_platform": "Flight platform",
    "dataset_groups": "Derived file groups",
    "research_area": "Research area",
}


def _snippet(text: str, terms: list[str], radius: int = 180) -> str:
    normalized = normalize_space(text)
    if not normalized:
        return ""
    lowered = normalized.lower()
    position = min(
        (lowered.find(term) for term in terms if lowered.find(term) >= 0),
        default=-1,
    )
    if position < 0:
        return normalized[: radius * 2]
    start = max(0, position - radius // 2)
    end = min(len(normalized), position + radius)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(normalized) else ""
    return f"{prefix}{normalized[start:end].strip()}{suffix}"


def _idf_table(records: list[dict[str, Any]], terms: list[str]) -> dict[str, float]:
    total = len(records) or 1
    frequencies = {term: 0 for term in terms}
    for record in records:
        haystack = " ".join(_field_text(record).values()).lower()
        for term in terms:
            if term in haystack:
                frequencies[term] += 1
    return {
        term: math.log((total + 1) / (frequency + 0.5))
        for term, frequency in frequencies.items()
    }


def retrieve(query: str, limit: int = 4) -> list[dict[str, Any]]:
    terms = list(dict.fromkeys(_tokenize(query)))
    if not terms:
        return []

    records = store.all_investigations()
    idf = _idf_table(records, terms)

    scored: list[dict[str, Any]] = []
    for record in records:
        fields = _field_text(record)
        total_score = 0.0
        matched_terms: set[str] = set()
        best_field = None
        best_field_score = 0.0

        for field, text in fields.items():
            lowered = text.lower()
            weight = FIELD_WEIGHTS.get(field, 1.0)
            field_score = 0.0
            for term in terms:
                occurrences = lowered.count(term)
                if occurrences:
                    matched_terms.add(term)
                    field_score += idf.get(term, 0.0) * weight * min(occurrences, 3)
            if field_score > best_field_score:
                best_field_score = field_score
                best_field = field
            total_score += field_score

        if total_score <= 0 or best_field is None:
            continue

        scored.append(
            {
                "investigation_id": record["investigation_id"],
                "title": record.get("title") or record["investigation_id"],
                "field": FIELD_LABELS.get(best_field, best_field),
                "snippet": _snippet(fields[best_field], sorted(matched_terms)),
                "score": round(total_score, 4),
                "matched_terms": sorted(matched_terms),
            }
        )

    scored.sort(key=lambda item: (-item["score"], item["investigation_id"]))
    return scored[:limit]


def compose_answer(query: str, citations: list[dict[str, Any]]) -> str:
    if not citations:
        return (
            "The available NASA PSI investigation metadata does not contain enough "
            "evidence to answer this question. Try naming an investigation (for example "
            "PSI-25 or BASS-II), a research area, a platform, or a file format. "
            "No measurements were fabricated or inferred."
        )

    lines = [
        "Based on the available NASA PSI investigation metadata, the strongest matches are:",
        "",
    ]
    for citation in citations:
        lines.append(
            f"- **{citation['investigation_id']} - {citation['title']}** "
            f"(matched in {citation['field']}): {citation['snippet']}"
        )
    lines.extend(
        [
            "",
            "This answer is assembled from investigation descriptions and file-inventory "
            "metadata only. It does not compare or interpret experimental measurements.",
        ]
    )
    return "\n".join(lines)

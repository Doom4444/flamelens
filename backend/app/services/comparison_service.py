"""Metadata and file-inventory comparison between two investigations.

This service intentionally performs no measurement comparison. It returns an
explicit scope flag and notice so the API cannot imply scientific
comparability that the source data does not support.
"""

from __future__ import annotations

from typing import Any

from app.core.exceptions import EntityNotFoundException, ScientificAnalysisException
from app.data_pipeline.metadata_repository import store

COMPARED_FIELDS = (
    "investigation_id",
    "title",
    "acronym",
    "research_area",
    "sub_research_area",
    "project_type",
    "flight_platform",
    "experiment_hardware",
    "managing_nasa_center",
    "sponsoring_agency",
    "start_date_iso",
    "end_date_iso",
    "doi",
    "keywords",
    "related_investigations",
    "file_count",
    "dataset_count",
    "file_inventory_available",
)


def _compared(record: dict[str, Any]) -> dict[str, Any]:
    enriched = store.enrich_investigation(record)
    description = enriched.get("description") or {}
    payload = {field: enriched.get(field) for field in COMPARED_FIELDS}
    payload.update(
        {
            "objectives": description.get("objectives"),
            "approach": description.get("approach"),
            "hypothesis": description.get("hypothesis"),
            "research_impacts": description.get("research_impacts"),
            "storage": enriched.get("storage"),
            "format_distribution": enriched.get("format_distribution", {}),
            "format_category_distribution": enriched.get(
                "format_category_distribution", {}
            ),
        }
    )
    return payload


def compare(investigation_ids: list[str]) -> dict[str, Any]:
    normalized = [value.strip().upper() for value in investigation_ids if value.strip()]
    if len(normalized) < 2:
        raise ScientificAnalysisException(
            "Two investigation IDs are required for comparison.",
            details={"provided": normalized},
        )
    if len(set(normalized)) != len(normalized):
        raise ScientificAnalysisException(
            "Comparison requires two different investigations.",
            details={"provided": normalized},
        )
    if len(normalized) > 2:
        raise ScientificAnalysisException(
            "Only two investigations can be compared at a time.",
            details={"provided": normalized},
        )

    investigations = []
    for investigation_id in normalized:
        record = store.get_investigation(investigation_id)
        if record is None:
            raise EntityNotFoundException("Investigation", investigation_id)
        investigations.append(_compared(record))

    left, right = investigations

    keyword_index = {
        row["investigation_id"]: {keyword.lower(): keyword for keyword in row.get("keywords") or []}
        for row in investigations
    }
    shared_keyword_keys = set(keyword_index[left["investigation_id"]]) & set(
        keyword_index[right["investigation_id"]]
    )
    shared_keywords = sorted(
        {keyword_index[row["investigation_id"]][key] for row in investigations for key in shared_keyword_keys},
        key=str.lower,
    )

    category_left = left.get("format_category_distribution") or {}
    category_right = right.get("format_category_distribution") or {}
    categories = sorted(set(category_left) | set(category_right))
    format_overlap = {
        category: {
            left["investigation_id"]: category_left.get(category, 0),
            right["investigation_id"]: category_right.get(category, 0),
        }
        for category in categories
    }
    shared_formats = sorted(set(category_left) & set(category_right))

    storage_left = left.get("storage") or {}
    storage_right = right.get("storage") or {}
    inventory_deltas = {
        "file_count": {
            "difference": (left.get("file_count") or 0) - (right.get("file_count") or 0),
            "left": left.get("file_count") or 0,
            "right": right.get("file_count") or 0,
        },
        "dataset_count": {
            "difference": (left.get("dataset_count") or 0) - (right.get("dataset_count") or 0),
            "left": left.get("dataset_count") or 0,
            "right": right.get("dataset_count") or 0,
        },
        "remote_inventory_size_bytes": {
            "difference": int(storage_left.get("remote_inventory_size_bytes") or 0)
            - int(storage_right.get("remote_inventory_size_bytes") or 0),
            "left": int(storage_left.get("remote_inventory_size_bytes") or 0),
            "right": int(storage_right.get("remote_inventory_size_bytes") or 0),
        },
    }

    return {
        "comparison_scope": "metadata_and_file_inventory",
        "measurement_comparison_available": False,
        "notice": (
            "This comparison covers NASA PSI metadata and file inventory only. "
            "No experimental measurements are parsed or compared, and no scientific "
            "comparability between investigations is implied."
        ),
        "investigations": investigations,
        "shared_keywords": shared_keywords,
        "shared_formats": shared_formats,
        "format_overlap": format_overlap,
        "inventory_deltas": inventory_deltas,
    }

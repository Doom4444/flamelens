"""Investigation, file and storage queries for the metadata API."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import EntityNotFoundException
from app.data_pipeline.metadata_repository import paginate, sort_files, sort_investigations, store
from app.utils.formatting import human_bytes

SUMMARY_FIELDS = (
    "investigation_id",
    "title",
    "acronym",
    "research_area",
    "sub_research_area",
    "project_type",
    "flight_platform",
    "start_date_iso",
    "end_date_iso",
    "doi",
    "keywords",
    "description",
    "audit_level",
    "file_inventory_available",
    "dataset_count",
    "file_count",
    "file_counts",
    "storage",
)

EXPORT_COLUMNS = (
    "file_id",
    "investigation_id",
    "dataset_id",
    "dataset_name",
    "filename",
    "extension",
    "mime_type",
    "format_category",
    "size_bytes",
    "size_human",
    "download_status",
    "download_eligible",
    "manual_approval_required",
    "downloaded",
    "local_size_bytes",
    "empty_file",
    "psi_file_version",
    "remote_path",
    "s3_path",
    "download_url",
    "legacy_url_status",
    "restricted",
    "visible",
)


def _generated_at() -> str | None:
    return store.investigations_payload.get("generated_at_utc")


def _snapshot_at() -> str | None:
    return (store.investigations_payload.get("source") or {}).get("snapshot_captured_at_utc")


def to_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {field: record.get(field) for field in SUMMARY_FIELDS}


def get_investigation_or_404(investigation_id: str) -> dict[str, Any]:
    record = store.get_investigation(investigation_id)
    if record is None:
        raise EntityNotFoundException("Investigation", investigation_id)
    return record


def list_investigations(
    query: str | None = None,
    research_area: str | None = None,
    sub_research_area: str | None = None,
    flight_platform: str | None = None,
    audit_level: str | None = None,
    has_file_inventory: bool | None = None,
    sort_by: str = "id",
    order: str = "asc",
    page: int = 1,
    page_size: int = 12,
) -> dict[str, Any]:
    rows = store.search_investigations(
        query=query,
        research_area=research_area,
        sub_research_area=sub_research_area,
        flight_platform=flight_platform,
        audit_level=audit_level,
        has_file_inventory=has_file_inventory,
    )
    enriched = [store.enrich_investigation(record) for record in rows]
    enriched = sort_investigations(enriched, sort_by, order)
    summaries = [to_summary(record) for record in enriched]
    page_payload = paginate(summaries, page, page_size)

    all_records = store.all_investigations()
    facets = {
        "research_areas": sorted(
            {record.get("research_area") for record in all_records if record.get("research_area")}
        ),
        "sub_research_areas": sorted(
            {
                record.get("sub_research_area")
                for record in all_records
                if record.get("sub_research_area")
            }
        ),
        "flight_platforms": sorted(
            {record.get("flight_platform") for record in all_records if record.get("flight_platform")}
        ),
    }
    return {
        "items": page_payload["items"],
        "pagination": page_payload["pagination"],
        "filters": {
            "q": query,
            "research_area": research_area,
            "sub_research_area": sub_research_area,
            "flight_platform": flight_platform,
            "audit_level": audit_level,
            "has_file_inventory": has_file_inventory,
            "sort_by": sort_by,
            "order": order,
        },
        "facets": facets,
        "generated_at_utc": _generated_at(),
    }


def get_investigation_detail(investigation_id: str) -> dict[str, Any]:
    record = get_investigation_or_404(investigation_id)
    detail = store.enrich_investigation(record)
    detail["related_edges"] = store.related_edges(investigation_id)
    detail["data_gaps"] = store.gaps_for(investigation_id)
    return detail


def file_totals(files: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_extension: dict[str, int] = {}
    total_size = 0
    known = 0
    unknown = 0
    for record in files:
        status = record.get("download_status") or "UNKNOWN"
        by_status[status] = by_status.get(status, 0) + 1
        category = record.get("format_category") or "other"
        by_category[category] = by_category.get(category, 0) + 1
        extension = record.get("extension") or "(none)"
        by_extension[extension] = by_extension.get(extension, 0) + 1
        if record.get("size_known") and record.get("size_bytes") is not None:
            known += 1
            total_size += int(record.get("size_bytes") or 0)
        else:
            unknown += 1
    return {
        "total_items": len(files),
        "known_size_items": known,
        "unknown_size_items": unknown,
        "remote_size_bytes": total_size,
        "remote_size_human": human_bytes(total_size),
        "local_downloaded_size_bytes": 0,
        "local_downloaded_size_human": "0 B",
        "downloaded_items": 0,
        "by_status": dict(sorted(by_status.items())),
        "by_category": dict(sorted(by_category.items())),
        "by_extension": dict(sorted(by_extension.items())),
    }


def list_files(
    investigation_id: str | None = None,
    query: str | None = None,
    extension: str | None = None,
    format_category: str | None = None,
    download_status: str | None = None,
    dataset_id: str | None = None,
    min_size: int | None = None,
    max_size: int | None = None,
    sort_by: str = "filename",
    order: str = "asc",
    page: int = 1,
    page_size: int = 25,
) -> dict[str, Any]:
    if investigation_id:
        get_investigation_or_404(investigation_id)
    rows = store.search_files(
        investigation_id=investigation_id,
        query=query,
        extension=extension,
        format_category=format_category,
        download_status=download_status,
        dataset_id=dataset_id,
        min_size=min_size,
        max_size=max_size,
    )
    rows = sort_files(rows, sort_by, order)
    totals = file_totals(rows)
    page_payload = paginate(rows, page, page_size)
    return {
        "items": page_payload["items"],
        "pagination": page_payload["pagination"],
        "filters": {
            "investigation_id": investigation_id,
            "q": query,
            "extension": extension,
            "format_category": format_category,
            "download_status": download_status,
            "dataset_id": dataset_id,
            "min_size": min_size,
            "max_size": max_size,
            "sort_by": sort_by,
            "order": order,
        },
        "totals": totals,
    }


def export_rows(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in files:
        row = {column: record.get(column) for column in EXPORT_COLUMNS}
        row["size_human"] = human_bytes(record.get("size_bytes"))
        rows.append(row)
    return rows


def list_export_files(
    investigation_id: str | None = None,
    query: str | None = None,
    extension: str | None = None,
    format_category: str | None = None,
    download_status: str | None = None,
    dataset_id: str | None = None,
    sort_by: str = "filename",
    order: str = "asc",
) -> list[dict[str, Any]]:
    if investigation_id:
        get_investigation_or_404(investigation_id)
    rows = store.search_files(
        investigation_id=investigation_id,
        query=query,
        extension=extension,
        format_category=format_category,
        download_status=download_status,
        dataset_id=dataset_id,
    )
    return sort_files(rows, sort_by, order)


def get_storage_summary(investigation_id: str) -> dict[str, Any]:
    record = get_investigation_or_404(investigation_id)
    row = store.get_storage_row(investigation_id)
    if row is None:
        return {
            "investigation_id": record["investigation_id"],
            "title": record.get("title"),
            "acronym": record.get("acronym"),
            "dataset_count": 0,
            "file_counts": {},
            "storage": {
                "remote_inventory_size_bytes": 0,
                "remote_inventory_size_human": "0 B",
                "remote_inventory_complete": False,
                "remote_inventory_is_known_size_subtotal": True,
                "psi_reported_total_file_size_bytes": record.get(
                    "reported_total_file_size_bytes"
                ),
                "psi_reported_total_file_size_human": record.get(
                    "reported_total_file_size_human"
                ),
                "delta_vs_reported_bytes": None,
                "local_downloaded_size_bytes": 0,
                "local_downloaded_size_human": "0 B",
                "pending_download_size_bytes": 0,
                "pending_download_size_human": "0 B",
                "over_limit_size_bytes": 0,
                "over_limit_size_human": "0 B",
                "unknown_size_file_count": 0,
            },
            "format_distribution": {},
            "format_category_distribution": {},
            "historical_removed": {},
            "largest_files": [],
            "notes": ["No file inventory has been audited for this investigation yet."],
            "data_gaps": store.gaps_for(investigation_id),
        }
    payload = dict(row)
    payload["data_gaps"] = store.gaps_for(investigation_id)
    return payload


def get_datasets(investigation_id: str) -> dict[str, Any]:
    get_investigation_or_404(investigation_id)
    datasets = store.get_datasets(investigation_id)
    return {
        "investigation_id": investigation_id.upper(),
        "items": datasets,
        "total_items": len(datasets),
        "total_size_bytes": sum(int(item.get("total_size_bytes") or 0) for item in datasets),
        "method": store.datasets_payload.get("method", {}),
    }


__all__ = [
    "to_summary",
    "get_investigation_or_404",
    "list_investigations",
    "get_investigation_detail",
    "list_files",
    "export_rows",
    "list_export_files",
    "get_storage_summary",
    "get_datasets",
    "file_totals",
    "_snapshot_at",
]

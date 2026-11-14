"""Dashboard and storage analytics derived from the audit inventories."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.data_pipeline.metadata_repository import store
from app.services.investigation_service import to_summary
from app.utils.formatting import human_bytes, percent


def _files_by_extension() -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    sizes: Counter[str] = Counter()
    category: dict[str, str] = {}
    for record in store.all_files():
        extension = record.get("extension") or "(none)"
        counter[extension] += 1
        sizes[extension] += int(record.get("size_bytes") or 0)
        category[extension] = record.get("format_category") or "other"
    total_bytes = sum(sizes.values()) or 1
    rows = [
        {
            "extension": extension,
            "format_category": category.get(extension, "other"),
            "count": count,
            "size_bytes": sizes[extension],
            "size_human": human_bytes(sizes[extension]),
            "share_of_bytes": percent(sizes[extension], total_bytes),
        }
        for extension, count in counter.items()
    ]
    return sorted(rows, key=lambda item: (-item["size_bytes"], item["extension"]))


def _files_by_category() -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    sizes: Counter[str] = Counter()
    for record in store.all_files():
        category = record.get("format_category") or "other"
        counter[category] += 1
        sizes[category] += int(record.get("size_bytes") or 0)
    total_bytes = sum(sizes.values()) or 1
    rows = [
        {
            "format_category": category,
            "count": count,
            "size_bytes": sizes[category],
            "size_human": human_bytes(sizes[category]),
            "share_of_bytes": percent(sizes[category], total_bytes),
        }
        for category, count in counter.items()
    ]
    return sorted(rows, key=lambda item: (-item["size_bytes"], item["format_category"]))


def _download_status_distribution() -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    sizes: Counter[str] = Counter()
    for record in store.all_files():
        status = record.get("download_status") or "UNKNOWN"
        counter[status] += 1
        sizes[status] += int(record.get("size_bytes") or 0)
    return [
        {
            "download_status": status,
            "count": count,
            "size_bytes": sizes[status],
            "size_human": human_bytes(sizes[status]),
        }
        for status, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _research_area_distribution() -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    with_inventory: Counter[str] = Counter()
    for record in store.all_investigations():
        area = record.get("research_area") or "Unspecified"
        counts[area] += 1
        if record.get("file_inventory_available"):
            with_inventory[area] += 1
    return [
        {
            "research_area": area,
            "investigation_count": count,
            "with_file_inventory": with_inventory[area],
        }
        for area, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def overview() -> dict[str, Any]:
    global_storage = store.storage_payload.get("global", {})
    counts = store.files_payload.get("counts", {})
    investigations = store.all_investigations()
    pilots = [record for record in investigations if record.get("file_inventory_available")]
    featured = [
        to_summary(store.enrich_investigation(record))
        for record in sorted(
            pilots,
            key=lambda row: -(
                (store.get_storage_row(row["investigation_id"]) or {})
                .get("storage", {})
                .get("remote_inventory_size_bytes", 0)
            ),
        )
    ]

    return {
        "generated_at_utc": store.investigations_payload.get("generated_at_utc"),
        "snapshot_captured_at_utc": (store.investigations_payload.get("source") or {}).get(
            "snapshot_captured_at_utc"
        ),
        "data_source": "NASA PSI Stage 1 audit inventories",
        "totals": {
            "investigations": len(investigations),
            "investigations_with_file_inventory": global_storage.get(
                "investigations_with_file_inventory", len(pilots)
            ),
            "investigations_without_file_inventory": global_storage.get(
                "investigations_without_file_inventory", len(investigations) - len(pilots)
            ),
            "dataset_groups": global_storage.get("dataset_groups", 0),
            "files": counts.get("current_files", len(store.all_files())),
            "remote_inventory_size_bytes": global_storage.get("remote_inventory_size_bytes", 0),
            "remote_inventory_size_human": global_storage.get("remote_inventory_size_human"),
            "psi_reported_total_file_size_bytes": global_storage.get(
                "psi_reported_total_file_size_bytes"
            ),
            "psi_reported_total_file_size_human": global_storage.get(
                "psi_reported_total_file_size_human"
            ),
            "delta_vs_reported_bytes": global_storage.get("delta_vs_reported_bytes"),
            "local_downloaded_size_bytes": 0,
            "local_downloaded_size_human": "0 B",
            "downloaded_files": counts.get("downloaded_files", 0),
            "download_eligible_files": counts.get("download_eligible_files", 0),
            "over_limit_files": counts.get("over_limit_files", 0),
            "zero_byte_files": counts.get("zero_byte_files", 0),
            "historical_removed_files": counts.get("historical_removed_files", 0),
            "data_gap_count": len(store.data_gaps()),
        },
        "file_type_distribution": _files_by_extension(),
        "format_category_distribution": _files_by_category(),
        "download_status_distribution": _download_status_distribution(),
        "research_area_distribution": _research_area_distribution(),
        "featured_investigations": featured,
        "download_policy": store.files_payload.get("download_policy", {}),
        "data_notes": [
            "Remote inventory size is the sum of file sizes reported by NASA PSI. "
            "It is not local storage.",
            "No scientific files have been downloaded; local downloaded size is 0 B.",
            "Dataset groups are FlameLens-derived from filename category and PSI "
            "subcategory, not NASA-issued dataset identifiers.",
            "PSI-99 exposes only 2 files although NASA PSI reports a much larger total; "
            "its inventory is flagged incomplete.",
        ],
    }


def storage_analytics() -> dict[str, Any]:
    global_storage = store.storage_payload.get("global", {})
    rows = [dict(row) for row in store.storage_rows()]
    remote_total = int(global_storage.get("remote_inventory_size_bytes") or 0) or 1

    for row in rows:
        storage = row.get("storage", {})
        storage["share_of_remote_bytes"] = percent(
            storage.get("remote_inventory_size_bytes", 0), remote_total
        )
        row["storage"] = storage

    return {
        "generated_at_utc": store.storage_payload.get("generated_at_utc"),
        "snapshot_captured_at_utc": (store.investigations_payload.get("source") or {}).get(
            "snapshot_captured_at_utc"
        ),
        "global": {
            **global_storage,
            "local_downloaded_size_bytes": 0,
            "local_downloaded_size_human": "0 B",
        },
        "investigations": rows,
        "investigations_without_file_inventory": store.storage_payload.get(
            "investigations_without_file_inventory", []
        ),
        "file_type_distribution": _files_by_extension(),
        "format_category_distribution": _files_by_category(),
        "download_policy": store.files_payload.get("download_policy", {}),
        "data_gaps": store.data_gaps(),
        "units": store.storage_payload.get("units", {}),
    }

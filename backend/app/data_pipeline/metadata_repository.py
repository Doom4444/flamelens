"""Read-only data-access layer over the Stage 1 NASA PSI JSON inventories.

The API deliberately depends on this repository instead of importing JSON
files directly. Swapping the JSON store for PostgreSQL later therefore means
replacing this module only; routes and response schemas stay untouched.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_METADATA_DIR = REPO_ROOT / "data" / "metadata"

INVESTIGATIONS_FILE = "investigations_inventory.json"
DATASETS_FILE = "datasets_inventory.json"
FILES_FILE = "files_inventory.json"
STORAGE_FILE = "storage_summary.json"


def _metadata_dir() -> Path:
    override = os.environ.get("FLAMELENS_METADATA_DIR")
    return Path(override).resolve() if override else DEFAULT_METADATA_DIR


class MetadataStore:
    """Loads and indexes the four audit inventories once per process."""

    def __init__(self, metadata_dir: Path | None = None) -> None:
        self.metadata_dir = Path(metadata_dir) if metadata_dir else _metadata_dir()
        # Re-entrant: _ensure_indexes holds the lock while payload properties
        # call _load(), which also needs it.
        self._lock = threading.RLock()
        self._payloads: dict[str, dict[str, Any]] = {}
        self._mtimes: dict[str, int] = {}
        self._indexes: dict[str, Any] = {}
        self._indexed = False

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def _load(self, filename: str) -> dict[str, Any]:
        path = self.metadata_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Metadata inventory not found: {path}")
        mtime = path.stat().st_mtime_ns
        with self._lock:
            if self._payloads.get(filename) is None or self._mtimes.get(filename) != mtime:
                self._payloads[filename] = json.loads(path.read_text(encoding="utf-8"))
                self._mtimes[filename] = mtime
                self._indexed = False
            return self._payloads[filename]

    @property
    def investigations_payload(self) -> dict[str, Any]:
        return self._load(INVESTIGATIONS_FILE)

    @property
    def datasets_payload(self) -> dict[str, Any]:
        return self._load(DATASETS_FILE)

    @property
    def files_payload(self) -> dict[str, Any]:
        return self._load(FILES_FILE)

    @property
    def storage_payload(self) -> dict[str, Any]:
        return self._load(STORAGE_FILE)

    def reload(self) -> None:
        """Force a fresh read on the next access (used by tests/dev)."""
        with self._lock:
            self._payloads.clear()
            self._mtimes.clear()
            self._indexes.clear()
            self._indexed = False

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------
    def _ensure_indexes(self) -> dict[str, Any]:
        with self._lock:
            if self._indexed:
                return self._indexes

            investigations = self.investigations_payload.get("investigations", [])
            datasets = self.datasets_payload.get("datasets", [])
            files = self.files_payload.get("files", [])
            removed = self.files_payload.get("historical_removed_files", [])
            storage_rows = self.storage_payload.get("investigations", [])

            datasets_by_inv: dict[str, list[dict[str, Any]]] = {}
            for dataset in datasets:
                datasets_by_inv.setdefault(dataset["investigation_id"], []).append(dataset)

            files_by_inv: dict[str, list[dict[str, Any]]] = {}
            for record in files:
                files_by_inv.setdefault(record["investigation_id"], []).append(record)

            self._indexes = {
                "investigations": investigations,
                "investigations_by_id": {row["investigation_id"]: row for row in investigations},
                "datasets": datasets,
                "datasets_by_inv": datasets_by_inv,
                "files": files,
                "files_by_inv": files_by_inv,
                "removed": removed,
                "storage_by_id": {row["investigation_id"]: row for row in storage_rows},
                "storage_rows": storage_rows,
                "data_gaps": self.storage_payload.get("data_gaps", []),
                "relationships": self.investigations_payload.get("relationships", []),
            }
            self._indexed = True
            return self._indexes

    # ------------------------------------------------------------------
    # Investigation access
    # ------------------------------------------------------------------
    def all_investigations(self) -> list[dict[str, Any]]:
        return self._ensure_indexes()["investigations"]

    def all_files(self) -> list[dict[str, Any]]:
        return self._ensure_indexes()["files"]

    def removed_files(self) -> list[dict[str, Any]]:
        return self._ensure_indexes()["removed"]

    def storage_rows(self) -> list[dict[str, Any]]:
        return self._ensure_indexes()["storage_rows"]

    def data_gaps(self) -> list[dict[str, Any]]:
        return self._ensure_indexes()["data_gaps"]

    def get_investigation(self, investigation_id: str) -> dict[str, Any] | None:
        return self._ensure_indexes()["investigations_by_id"].get(investigation_id.upper())

    def get_storage_row(self, investigation_id: str) -> dict[str, Any] | None:
        return self._ensure_indexes()["storage_by_id"].get(investigation_id.upper())

    def get_datasets(self, investigation_id: str) -> list[dict[str, Any]]:
        return self._ensure_indexes()["datasets_by_inv"].get(investigation_id.upper(), [])

    def get_files(self, investigation_id: str) -> list[dict[str, Any]]:
        return self._ensure_indexes()["files_by_inv"].get(investigation_id.upper(), [])

    # ------------------------------------------------------------------
    # Enrichment
    # ------------------------------------------------------------------
    def enrich_investigation(self, record: dict[str, Any]) -> dict[str, Any]:
        """Attach inventory-derived counts without mutating the raw record."""
        investigation_id = record["investigation_id"]
        enriched = dict(record)
        storage_row = self.get_storage_row(investigation_id)
        datasets = self.get_datasets(investigation_id)

        if storage_row:
            file_counts = storage_row.get("file_counts", {})
            storage = storage_row.get("storage", {})
            enriched.update(
                {
                    "dataset_count": storage_row.get("dataset_count", len(datasets)),
                    "file_count": file_counts.get("total_discovered", 0),
                    "file_counts": file_counts,
                    "storage": storage,
                    "format_distribution": storage_row.get("format_distribution", {}),
                    "format_category_distribution": storage_row.get(
                        "format_category_distribution", {}
                    ),
                    "historical_removed": storage_row.get("historical_removed", {}),
                    "storage_notes": storage_row.get("notes", []),
                    "file_inventory_available": True,
                }
            )
        else:
            enriched.update(
                {
                    "dataset_count": 0,
                    "file_count": 0,
                    "file_counts": {},
                    "storage": None,
                    "format_distribution": {},
                    "format_category_distribution": {},
                    "historical_removed": {},
                    "storage_notes": [],
                    "file_inventory_available": bool(record.get("file_inventory_available")),
                }
            )

        enriched["dataset_groups"] = datasets
        return enriched

    def related_edges(self, investigation_id: str) -> list[dict[str, str]]:
        investigation_id = investigation_id.upper()
        return [
            edge
            for edge in self._ensure_indexes()["relationships"]
            if edge["source"] == investigation_id or edge["target"] == investigation_id
        ]

    def gaps_for(self, investigation_id: str) -> list[dict[str, Any]]:
        investigation_id = investigation_id.upper()
        return [
            gap
            for gap in self.data_gaps()
            if investigation_id in str(gap.get("investigation_id", ""))
            or gap.get("investigation_id") == "ALL"
            or ("non-pilot" in str(gap.get("investigation_id", "")).lower() and not self.get_storage_row(investigation_id))
        ]

    # ------------------------------------------------------------------
    # Search primitives
    # ------------------------------------------------------------------
    @staticmethod
    def _tokens(query: str | None) -> list[str]:
        return [token.lower() for token in (query or "").split() if token]

    @staticmethod
    def _matches(tokens: list[str], haystack: str) -> bool:
        if not tokens:
            return True
        lowered = haystack.lower()
        return all(token in lowered for token in tokens)

    def search_investigations(
        self,
        query: str | None = None,
        research_area: str | None = None,
        sub_research_area: str | None = None,
        flight_platform: str | None = None,
        audit_level: str | None = None,
        has_file_inventory: bool | None = None,
    ) -> list[dict[str, Any]]:
        tokens = self._tokens(query)
        results: list[dict[str, Any]] = []
        for record in self.all_investigations():
            if research_area and record.get("research_area") != research_area:
                continue
            if sub_research_area and record.get("sub_research_area") != sub_research_area:
                continue
            if flight_platform and record.get("flight_platform") != flight_platform:
                continue
            if audit_level and record.get("audit_level") != audit_level:
                continue
            if has_file_inventory is not None and bool(record.get("file_inventory_available")) != has_file_inventory:
                continue

            description = record.get("description") or {}
            haystack = " ".join(
                str(part or "")
                for part in (
                    record.get("investigation_id"),
                    record.get("title"),
                    record.get("acronym"),
                    record.get("research_area"),
                    record.get("sub_research_area"),
                    record.get("flight_platform"),
                    record.get("proposal_title"),
                    " ".join(record.get("keywords") or []),
                    description.get("objectives"),
                    description.get("approach"),
                    description.get("hypothesis"),
                    description.get("research_impacts"),
                )
            )
            if self._matches(tokens, haystack):
                results.append(record)
        return results

    def search_files(
        self,
        investigation_id: str | None = None,
        query: str | None = None,
        extension: str | None = None,
        format_category: str | None = None,
        download_status: str | None = None,
        dataset_id: str | None = None,
        min_size: int | None = None,
        max_size: int | None = None,
    ) -> list[dict[str, Any]]:
        tokens = self._tokens(query)
        source = self.get_files(investigation_id) if investigation_id else self.all_files()
        results: list[dict[str, Any]] = []
        for record in source:
            if extension and (record.get("extension") or "").lower() != extension.lower():
                continue
            if format_category and record.get("format_category") != format_category:
                continue
            if download_status and record.get("download_status") != download_status:
                continue
            if dataset_id and record.get("dataset_id") != dataset_id:
                continue
            size = record.get("size_bytes") or 0
            if min_size is not None and size < min_size:
                continue
            if max_size is not None and size > max_size:
                continue
            haystack = " ".join(
                str(part or "")
                for part in (
                    record.get("investigation_id"),
                    record.get("filename"),
                    record.get("dataset_name"),
                    record.get("extension"),
                    record.get("mime_type"),
                    record.get("format_category"),
                )
            )
            if self._matches(tokens, haystack):
                results.append(record)
        return results


def _id_number(investigation_id: str) -> int:
    try:
        return int(investigation_id.split("-")[1])
    except (IndexError, ValueError):
        return 0


def sort_investigations(rows: Iterable[dict[str, Any]], sort_by: str, order: str) -> list[dict[str, Any]]:
    reverse = order.lower() == "desc"

    def key(record: dict[str, Any]) -> Any:
        if sort_by == "title":
            return (record.get("title") or "").lower()
        if sort_by == "start_date":
            return record.get("start_date_iso") or ""
        if sort_by == "end_date":
            return record.get("end_date_iso") or ""
        if sort_by == "file_count":
            return record.get("file_count") or 0
        if sort_by == "remote_size":
            return (record.get("storage") or {}).get("remote_inventory_size_bytes") or 0
        return _id_number(record.get("investigation_id", ""))

    return sorted(rows, key=key, reverse=reverse)


def sort_files(rows: Iterable[dict[str, Any]], sort_by: str, order: str) -> list[dict[str, Any]]:
    reverse = order.lower() == "desc"

    def key(record: dict[str, Any]) -> Any:
        if sort_by == "size":
            return record.get("size_bytes") or 0
        if sort_by == "extension":
            return (record.get("extension") or "").lower()
        if sort_by == "dataset":
            return (record.get("dataset_name") or "").lower()
        if sort_by == "investigation":
            return (_id_number(record.get("investigation_id", "")), record.get("filename") or "")
        return (record.get("filename") or "").lower()

    return sorted(rows, key=key, reverse=reverse)


def paginate(rows: list[Any], page: int, page_size: int) -> dict[str, Any]:
    total = len(rows)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, page)
    start = (page - 1) * page_size
    items = rows[start : start + page_size]
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        },
    }


# Shared singleton used by the API layer.
store = MetadataStore()

#!/usr/bin/env python3
"""Generate the Stage 1 NASA PSI data-source audit inventories.

This script is read-only with respect to the NASA PSI API: it consumes the
checked-in JSON snapshot under ``data/metadata/psi_api/`` and writes four
machine-readable inventories plus a console summary. It never downloads
scientific data files.

Usage
-----
    python scripts/audit_psi_source.py
    python scripts/audit_psi_source.py --check
    MAX_FILE_SIZE_MB=250 python scripts/audit_psi_source.py --check

Outputs
-------
    data/metadata/investigations_inventory.json
    data/metadata/datasets_inventory.json
    data/metadata/files_inventory.json
    data/metadata/storage_summary.json

Exit codes
----------
    0  success (and all reconciliation checks passed with --check)
    1  reconciliation failure or missing snapshot
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
METADATA_DIR = ROOT / "data" / "metadata"
SNAPSHOT_DIR = METADATA_DIR / "psi_api"
DESCRIPTIONS_PATH = METADATA_DIR / "psi_descriptions.jsonl"

PILOT_IDS = ["PSI-25", "PSI-26", "PSI-98", "PSI-99", "PSI-100", "PSI-101", "PSI-102"]

PSI_API_BASE = "https://psi.nasa.gov/geode-py/ws"
INVESTIGATION_ENDPOINT = f"{PSI_API_BASE}/repo/investigations/{{investigation_id}}"
SEARCH_ENDPOINT = f"{PSI_API_BASE}/repo/search?term=combustion&size=100"
DOWNLOAD_ENDPOINT_TEMPLATE = (
    PSI_API_BASE
    + "/studies/{investigation_id}/download"
    + "?file={quoted_filename}&version={version}&redirect=false"
)

MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
SCHEMA_VERSION = "1.0"

# Deterministic MIME map for every extension observed in the PSI pilots.
# Avoids platform-dependent ``mimetypes`` results.
MIME_TYPES = {
    ".csv": "text/csv",
    ".tsv": "text/tab-separated-values",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".txt": "text/plain",
    ".rtf": "application/rtf",
    ".json": "application/json",
    ".xml": "application/xml",
    ".h5": "application/x-hdf5",
    ".hdf5": "application/x-hdf5",
    ".nc": "application/x-netcdf",
    ".fits": "application/fits",
    ".dat": "application/octet-stream",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".bmp": "image/bmp",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".wmv": "video/x-ms-wmv",
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
    ".tgz": "application/gzip",
    ".rar": "application/vnd.rar",
    ".7z": "application/x-7z-compressed",
}

FORMAT_CATEGORIES = {
    "structured": {".csv", ".tsv", ".xls", ".xlsx", ".ods"},
    "document": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".ppt", ".pptx", ".odt", ".md"},
    "scientific": {".json", ".xml", ".h5", ".hdf5", ".nc", ".fits", ".dat"},
    "image": {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".m4v", ".mpeg", ".mpg"},
    "archive": {".zip", ".tar", ".gz", ".tgz", ".rar", ".7z", ".bz2", ".xz"},
}

# PSI exposes no dataset entity. Logical datasets are derived from the
# top-level PSI file category embedded in the filename plus the PSI
# ``subcategory`` field (experiment/run label). This is documented as a
# derived grouping, never as a PSI-authored dataset.
DATASET_DERIVATION = "top_level_filename_category + psi_subcategory"

MISSING = {"", None}


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def human_bytes(size: int | float | None) -> str | None:
    """Binary unit formatting (1 KB = 1024 B) used everywhere in the audit."""
    if size is None:
        return None
    size = int(size)
    for unit, divisor in (("TB", 1024**4), ("GB", 1024**3), ("MB", 1024**2), ("KB", 1024)):
        if size >= divisor:
            return f"{size / divisor:.3f} {unit}"
    return f"{size} B"


def normalize_space(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()


def split_keywords(value: str | None) -> list[str]:
    text = (value or "").replace("\n", " ").strip()
    if not text:
        return []
    parts = [p.strip() for p in re.split(r"\s{2,}|;", text) if p.strip()]
    return parts


def extract_psi_ids(value: str | None) -> list[str]:
    seen: list[str] = []
    for match in re.findall(r"PSI-\d+", value or ""):
        if match not in seen:
            seen.append(match)
    return seen


def parse_psi_date(value: Any) -> str | None:
    """Return an ISO-8601 UTC timestamp for PSI date-ish values.

    Handles Mongo ``{"$date": ms}`` wrappers, epoch seconds/milliseconds and
    the PSI textual ``MM-DD-YYYY`` format.
    """
    if value is None:
        return None
    if isinstance(value, dict):
        if "$date" not in value:
            return None
        value = value["$date"]
    if isinstance(value, (int, float)):
        number = float(value)
        seconds = number / 1000.0 if abs(number) > 1e11 else number
        try:
            return datetime.fromtimestamp(seconds, timezone.utc).replace(microsecond=0).isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    if not text:
        return None
    for pattern in ("%m-%d-%Y", "%d-%b-%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            parsed = datetime.strptime(text, pattern)
            return parsed.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    return None


def iso_date(value: str | None) -> str | None:
    return value[:10] if value else None


def extension_of(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    return suffix or ""


def format_category(extension: str) -> str:
    for category, extensions in FORMAT_CATEGORIES.items():
        if extension in extensions:
            return category
    return "other"


def top_level_category(investigation_id: str, filename: str) -> str:
    prefix = filename[len(investigation_id) + 1 :] if filename.startswith(investigation_id + "_") else filename
    if "_" in prefix:
        return prefix.split("_", 1)[0].strip() or "(root)"
    return "(root)"


def normalize_subcategory(value: str | None) -> str:
    """Trim and collapse whitespace around '/' so run labels group consistently."""
    return re.sub(r"\s*/\s*", "/", (value or "").strip())


def dataset_identity(investigation_id: str, filename: str, subcategory: str | None) -> tuple[str, str, str]:
    category = top_level_category(investigation_id, filename)
    sub = normalize_subcategory(subcategory)
    key = f"{investigation_id}|{category}|{sub}"
    return f"fld_{sha1(key)[:12]}", category, sub


def build_download_url(investigation_id: str, filename: str, version: Any) -> str:
    return DOWNLOAD_ENDPOINT_TEMPLATE.format(
        investigation_id=investigation_id,
        quoted_filename=quote(filename, safe=""),
        version=version,
    )


def legacy_url_status(url: str | None) -> str:
    if not url:
        return "NOT_PROVIDED"
    if "psi.ndc.nasa.gov" in url:
        return "DEAD_HOST_DNS_FAILURE"
    if url.startswith("/datamanager/"):
        return "RELATIVE_PATH_404"
    return "UNVERIFIED"


def unique_preserving_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_manifest() -> dict[str, Any]:
    path = SNAPSHOT_DIR / "manifest.json"
    if not path.exists():
        raise SystemExit(f"Missing PSI API snapshot manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_search_snapshot() -> dict[str, Any]:
    path = SNAPSHOT_DIR / "search_combustion.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    hits = payload["hits"]["hits"]
    sources = {hit["_source"]["Accession"]: hit["_source"] for hit in hits}
    return {
        "total": payload["hits"]["total"],
        "order": [hit["_source"]["Accession"] for hit in hits],
        "sources": sources,
    }


def load_pilot_payloads() -> dict[str, dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    for investigation_id in PILOT_IDS:
        path = SNAPSHOT_DIR / "investigations" / f"{investigation_id}.json"
        if not path.exists():
            raise SystemExit(f"Missing pilot snapshot: {path}")
        payloads[investigation_id] = json.loads(path.read_text(encoding="utf-8"))
    return payloads


def load_descriptions() -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    records: dict[str, dict[str, Any]] = {}
    counts: Counter[str] = Counter()
    if not DESCRIPTIONS_PATH.exists():
        return records, counts
    for line in DESCRIPTIONS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        investigation_id = record["investigation_id"]
        counts[investigation_id] += 1
        records.setdefault(investigation_id, record)
    return records, dict(counts)


def snapshot_hash(kind: str, investigation_id: str | None = None) -> str | None:
    if kind == "investigation" and investigation_id:
        path = SNAPSHOT_DIR / "investigations" / f"{investigation_id}.json"
    else:
        path = SNAPSHOT_DIR / "search_combustion.json"
    return sha256_file(path) if path.exists() else None


# ---------------------------------------------------------------------------
# Investigation inventory
# ---------------------------------------------------------------------------


def build_description(payload: dict[str, Any], source: dict[str, Any]) -> dict[str, str | None]:
    if payload:
        return {
            "objectives": normalize_space(payload.get("objective")) or None,
            "approach": normalize_space(payload.get("approach")) or None,
            "hypothesis": normalize_space(payload.get("hypothesis")) or None,
            "research_impacts": normalize_space(payload.get("researchImpacts")) or None,
        }
    return {
        "objectives": normalize_space(source.get("Objectives")) or None,
        "approach": normalize_space(source.get("Approach")) or None,
        "hypothesis": normalize_space(source.get("Hypothesis")) or None,
        "research_impacts": normalize_space(source.get("Research Impacts/Earth Benefits")) or None,
    }


def build_investigations(
    search: dict[str, Any],
    pilots: dict[str, dict[str, Any]],
    descriptions: dict[str, dict[str, Any]],
    description_counts: dict[str, int],
    generated_at: str,
) -> dict[str, Any]:
    investigation_rows: list[dict[str, Any]] = []
    relationships: list[dict[str, str]] = []

    for investigation_id in search["order"]:
        source = search["sources"][investigation_id]
        payload = pilots.get(investigation_id)
        is_pilot = payload is not None

        description = build_description(payload or {}, source)
        related = unique_preserving_order(
            extract_psi_ids(
                (payload or {}).get("related_glds")
                if is_pilot
                else source.get("Related Investigations")
            )
        )
        related = [item for item in related if item != investigation_id]

        if is_pilot:
            hardware = payload.get("experimentHardware")
            hardware_link = payload.get("experimentHardwareLink")
            contacts = [
                {
                    "name": normalize_space(
                        " ".join(
                            part
                            for part in (
                                contact.get("firstName"),
                                contact.get("midInitials"),
                                contact.get("lastName"),
                            )
                            if part
                        )
                    ),
                    "email": contact.get("email") or None,
                    "affiliation": contact.get("affiliation") or None,
                    "roles": [
                        normalize_space(role.get("annotationValue"))
                        for role in contact.get("roles") or []
                        if normalize_space(role.get("annotationValue"))
                    ],
                }
                for contact in payload.get("contacts") or []
            ]
            publications = [
                {
                    "title": normalize_space(publication.get("title")) or None,
                    "authors": normalize_space(publication.get("authorList")) or None,
                    "doi": publication.get("doi") or None,
                    "pubmed_id": publication.get("pubMedID") or None,
                }
                for publication in payload.get("publications") or []
            ]
            publication_titles_structured = True
            reported_total = payload.get("totalFileSize")
            version = payload.get("version")
            keyword_source = source.get("Keywords")
            start_date_raw = payload.get("investigationStartDate") or source.get("Investigation Start Date")
            end_date_raw = payload.get("investigationEndDate") or source.get("Investigation End Date")
            proposal_title = payload.get("proposalTitle") or source.get("Proposal Title")
            research_area = payload.get("researchArea") or source.get("Research Area")
            sub_research_area = payload.get("subResearchArea") or source.get("SubResearch Area")
            flight_platform = payload.get("flightProgram") or source.get("Flight Platform")
            managing_center = payload.get("managingNasaCenter") or source.get("Monitoring Center")
            sponsoring_agency = payload.get("spaceProgram") or source.get("Sponsoring Agency")
            doi = payload.get("doi")
            data_source = "psi_repo_investigations_api"
            access_url = INVESTIGATION_ENDPOINT.format(investigation_id=investigation_id)
            contacts_available = bool(contacts)
        else:
            hardware_field = source.get("Experiment Hardware")
            if isinstance(hardware_field, dict):
                hardware = hardware_field.get("Name")
                hardware_link = hardware_field.get("Link")
            else:
                hardware = hardware_field
                hardware_link = None
            contacts = []
            publications = []
            publication_titles_structured = False
            reported_total = None
            version = None
            keyword_source = source.get("Keywords")
            start_date_raw = source.get("Investigation Start Date")
            end_date_raw = source.get("Investigation End Date")
            proposal_title = source.get("Proposal Title")
            research_area = source.get("Research Area")
            sub_research_area = source.get("SubResearch Area")
            flight_platform = source.get("Flight Platform")
            managing_center = source.get("Monitoring Center")
            sponsoring_agency = source.get("Sponsoring Agency")
            doi = None
            data_source = "psi_repo_search_api"
            access_url = SEARCH_ENDPOINT
            contacts_available = False

        field_presence = {
            "title": bool(normalize_space(source.get("Title"))),
            "acronym": bool(normalize_space(source.get("Acronym"))),
            "research_area": bool(normalize_space(research_area)),
            "sub_research_area": bool(normalize_space(sub_research_area)),
            "flight_platform": bool(normalize_space(flight_platform)),
            "start_date": bool(normalize_space(start_date_raw)),
            "end_date": bool(normalize_space(end_date_raw)),
            "proposal_title": bool(normalize_space(proposal_title)),
            "objectives": bool(description["objectives"]),
            "approach": bool(description["approach"]),
            "hypothesis": bool(description["hypothesis"]),
            "research_impacts": bool(description["research_impacts"]),
            "related_investigations": bool(related),
            "experiment_hardware": bool(normalize_space(hardware)),
            "contacts": contacts_available,
            "doi": bool(doi),
            "publication_titles": bool(publications)
            if publication_titles_structured
            else bool(normalize_space(source.get("Publication Title"))),
        }

        existing = descriptions.get(investigation_id)
        record = {
            "investigation_id": investigation_id,
            "title": normalize_space(source.get("Title")),
            "acronym": normalize_space(source.get("Acronym")) or None,
            "research_area": normalize_space(research_area) or None,
            "sub_research_area": normalize_space(sub_research_area) or None,
            "project_type": normalize_space(source.get("Project Type")) or None,
            "flight_platform": normalize_space(flight_platform) or None,
            "experiment_hardware": {
                "name": normalize_space(hardware) or None,
                "link": hardware_link or None,
            },
            "managing_nasa_center": normalize_space(managing_center) or None,
            "sponsoring_agency": normalize_space(sponsoring_agency) or None,
            "start_date_raw": start_date_raw or None,
            "start_date_iso": iso_date(parse_psi_date(start_date_raw)),
            "end_date_raw": end_date_raw or None,
            "end_date_iso": iso_date(parse_psi_date(end_date_raw)),
            "proposal_title": normalize_space(proposal_title) or None,
            "doi": doi or None,
            "keywords": split_keywords(keyword_source),
            "related_investigations": related,
            "contacts": contacts,
            "publications": publications,
            "publication_titles_structured": publication_titles_structured,
            "publication_titles_raw": normalize_space(source.get("Publication Title")) or None
            if not publication_titles_structured
            else None,
            "publication_authors_raw": normalize_space(source.get("Publication Author List")) or None
            if not publication_titles_structured
            else None,
            "description": description,
            "field_presence": field_presence,
            "audit_level": "full_audit" if is_pilot else "description_only",
            "file_inventory_available": is_pilot,
            "psi_api_url": access_url,
            "data_source": data_source,
            "psi_version": version,
            "reported_total_file_size_bytes": int(reported_total) if isinstance(reported_total, (int, float)) else None,
            "reported_total_file_size_human": human_bytes(reported_total),
            "existing_project_metadata": {
                "jsonl_record_present": existing is not None,
                "jsonl_record_count": description_counts.get(investigation_id, 0),
                "playwright_scrape_failed": investigation_id in {"PSI-10", "PSI-23", "PSI-39"},
            },
            "snapshot_sha256": snapshot_hash("investigation", investigation_id)
            if is_pilot
            else snapshot_hash("search"),
        }
        investigation_rows.append(record)

        for target in related:
            relationships.append({"source": investigation_id, "target": target, "type": "related_investigation"})

    # Drop relationship edges that point outside the combustion result set but
    # keep them visible in a dedicated field.
    known = {row["investigation_id"] for row in investigation_rows}
    internal = [edge for edge in relationships if edge["target"] in known]
    external = [edge for edge in relationships if edge["target"] not in known]
    deduped_internal = list({(e["source"], e["target"]): e for e in internal}.values())

    field_totals = Counter()
    for row in investigation_rows:
        for field, present in row["field_presence"].items():
            field_totals[field] += int(bool(present))

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": generated_at,
        "description": (
            "Investigation-level inventory for the 26 combustion investigations returned by the "
            "official NASA PSI search API. Seven pilot investigations carry a complete file "
            "inventory; the remaining 19 carry official description metadata only."
        ),
        "source": {
            "api_base": PSI_API_BASE,
            "search_endpoint": SEARCH_ENDPOINT,
            "investigation_endpoint_template": INVESTIGATION_ENDPOINT,
            "download_endpoint_template": DOWNLOAD_ENDPOINT_TEMPLATE,
            "snapshot_directory": "data/metadata/psi_api/",
            "snapshot_captured_at_utc": load_manifest().get("captured_at_utc"),
            "search_total": search["total"],
        },
        "counts": {
            "total_investigations": len(investigation_rows),
            "full_audit": sum(1 for row in investigation_rows if row["audit_level"] == "full_audit"),
            "description_only": sum(1 for row in investigation_rows if row["audit_level"] == "description_only"),
            "with_file_inventory": sum(1 for row in investigation_rows if row["file_inventory_available"]),
            "with_structured_publications": sum(
                1 for row in investigation_rows if row["publication_titles_structured"]
            ),
            "existing_jsonl_records": sum(
                1 for row in investigation_rows if row["existing_project_metadata"]["jsonl_record_present"]
            ),
        },
        "field_completeness": {
            "total_investigations": len(investigation_rows),
            "counts": dict(sorted(field_totals.items())),
        },
        "relationships": sorted(deduped_internal, key=lambda edge: (edge["source"], edge["target"])),
        "external_relationship_targets": sorted(
            {edge["target"] for edge in external}, key=lambda value: int(value.split("-")[1])
        ),
        "investigations": investigation_rows,
    }


# ---------------------------------------------------------------------------
# Files, datasets and storage
# ---------------------------------------------------------------------------


def iter_current_arrays(payload: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    ordered: list[tuple[str, dict[str, Any]]] = []
    for field in ("added", "experimentalTable", "images", "modified"):
        for item in payload.get(field) or []:
            ordered.append((field, item))
    return ordered


def build_file_record(
    investigation_id: str,
    source_field: str,
    item: dict[str, Any],
    also_reported_in: list[str],
    generated_at: str,
) -> dict[str, Any]:
    filename = item.get("file_name") or ""
    extension = extension_of(filename)
    s3_path = item.get("s3_path") or item.get("remote_path") or filename
    size = item.get("file_size")
    size_known = isinstance(size, (int, float))
    size_bytes = int(size) if size_known else None
    dataset_id, category, subcategory = dataset_identity(investigation_id, filename, item.get("subcategory"))
    if size_known and size_bytes is not None:
        download_status = "OVER_LIMIT" if size_bytes > MAX_FILE_SIZE_BYTES else "PENDING"
    else:
        download_status = "UNKNOWN_SIZE"

    return {
        "file_id": f"flf_{sha1(f'{investigation_id}|{s3_path}')[:16]}",
        "investigation_id": investigation_id,
        "dataset_id": dataset_id,
        "dataset_name": f"{category} / {subcategory}" if subcategory else category,
        "lifecycle_status": "current",
        "filename": filename,
        "extension": extension or None,
        "mime_type": MIME_TYPES.get(extension, "application/octet-stream"),
        "format_category": format_category(extension),
        "psi_subcategory": subcategory or None,
        "description": None,
        "description_available": False,
        "source_fields": unique_preserving_order([source_field, *also_reported_in]),
        "remote_path": item.get("remote_path"),
        "s3_path": s3_path,
        "bucket": item.get("bucket"),
        "psi_file_version": item.get("version"),
        "size_bytes": size_bytes,
        "size_known": size_known,
        "empty_file": bool(size_known and size_bytes == 0),
        "download_url": build_download_url(investigation_id, filename, item.get("version")) if filename else None,
        "download_url_requires_signed_redirect": True,
        "legacy_remote_url": item.get("remote_url"),
        "legacy_url_status": legacy_url_status(item.get("remote_url")),
        "download_eligible": bool(size_known and size_bytes is not None and size_bytes <= MAX_FILE_SIZE_BYTES),
        "download_status": download_status,
        "manual_approval_required": download_status == "OVER_LIMIT",
        "downloaded": False,
        "local_size_bytes": None,
        "local_path": None,
        "sha256": None,
        "parsing_status": "NOT_PARSED",
        "restricted": bool(item.get("restricted")),
        "visible": item.get("visible") is not False,
        "psi_created_at_utc": parse_psi_date(item.get("date_created")),
        "psi_modified_at_utc": parse_psi_date(item.get("date_modified")),
        "discovered_at_utc": generated_at,
    }


def build_removed_record(investigation_id: str, item: dict[str, Any], generated_at: str) -> dict[str, Any]:
    record = build_file_record(investigation_id, "removed", item, [], generated_at)
    record.update(
        {
            "dataset_id": None,
            "dataset_name": None,
            "lifecycle_status": "removed_historical_version",
            "download_eligible": False,
            "download_status": "HISTORICAL_REMOVED",
            "manual_approval_required": False,
        }
    )
    return record


def build_files_and_datasets(
    pilots: dict[str, dict[str, Any]], generated_at: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    files: list[dict[str, Any]] = []
    removed_files: list[dict[str, Any]] = []
    datasets: dict[str, dict[str, Any]] = {}

    for investigation_id in PILOT_IDS:
        payload = pilots[investigation_id]
        seen: dict[str, dict[str, Any]] = {}

        for source_field, item in iter_current_arrays(payload):
            s3_path = item.get("s3_path") or item.get("remote_path") or item.get("file_name")
            if s3_path in seen:
                seen[s3_path]["_also"].append(source_field)
                continue
            seen[s3_path] = {"item": item, "source_field": source_field, "_also": []}

        for s3_path, entry in seen.items():
            record = build_file_record(
                investigation_id,
                entry["source_field"],
                entry["item"],
                entry["_also"],
                generated_at,
            )
            files.append(record)

            dataset = datasets.get(record["dataset_id"])
            if dataset is None:
                dataset = {
                    "dataset_id": record["dataset_id"],
                    "investigation_id": investigation_id,
                    "name": record["dataset_name"],
                    "top_level_category": top_level_category(investigation_id, record["filename"]),
                    "psi_subcategory": record["psi_subcategory"],
                    "description": None,
                    "description_available": False,
                    "derivation": DATASET_DERIVATION,
                    "file_count": 0,
                    "known_size_file_count": 0,
                    "total_size_bytes": 0,
                    "format_distribution": {},
                    "file_ids": [],
                }
                datasets[record["dataset_id"]] = dataset
            dataset["file_count"] += 1
            dataset["file_ids"].append(record["file_id"])
            if record["size_known"]:
                dataset["known_size_file_count"] += 1
                dataset["total_size_bytes"] += record["size_bytes"] or 0

        for item in payload.get("removed") or []:
            removed_files.append(build_removed_record(investigation_id, item, generated_at))

    for dataset in datasets.values():
        formats = Counter()
        for file_id in dataset["file_ids"]:
            match = next(record for record in files if record["file_id"] == file_id)
            formats[match["extension"] or "(none)"] += 1
        dataset["format_distribution"] = dict(sorted(formats.items()))

    datasets_sorted = sorted(
        datasets.values(),
        key=lambda item: (int(item["investigation_id"].split("-")[1]), item["name"]),
    )

    category_counts = Counter(record["format_category"] for record in files)
    extension_counts = Counter(record["extension"] or "(none)" for record in files)
    mime_counts = Counter(record["mime_type"] for record in files)

    files_inventory = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": generated_at,
        "description": (
            "Current file inventory for the seven audited pilot investigations. Files are deduplicated "
            "by PSI S3 path across the added/experimentalTable/images/modified arrays. Historical "
            "'removed' versions are listed separately and are not part of current storage totals."
        ),
        "download_policy": {
            "max_file_size_mb": MAX_FILE_SIZE_MB,
            "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
            "environment_variable": "MAX_FILE_SIZE_MB",
            "note": "Sizes above the limit are inventoried but never downloaded automatically.",
        },
        "counts": {
            "current_files": len(files),
            "current_known_size_files": sum(1 for record in files if record["size_known"]),
            "current_unknown_size_files": sum(1 for record in files if not record["size_known"]),
            "current_total_size_bytes": sum(record["size_bytes"] or 0 for record in files),
            "download_eligible_files": sum(1 for record in files if record["download_eligible"]),
            "over_limit_files": sum(1 for record in files if record["download_status"] == "OVER_LIMIT"),
            "zero_byte_files": sum(1 for record in files if record["empty_file"]),
            "downloaded_files": sum(1 for record in files if record["downloaded"]),
            "historical_removed_files": len(removed_files),
            "historical_removed_total_size_bytes": sum(record["size_bytes"] or 0 for record in removed_files),
        },
        "format_distribution": {
            "by_extension": dict(sorted(extension_counts.items())),
            "by_category": dict(sorted(category_counts.items())),
            "by_mime_type": dict(sorted(mime_counts.items())),
        },
        "files": files,
        "historical_removed_files": removed_files,
    }

    datasets_inventory = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": generated_at,
        "description": (
            "Logical dataset groups derived for the seven audited pilots. NASA PSI does not expose a "
            "dataset entity or dataset-level descriptions through its API; each group is therefore "
            "derived deterministically from the top-level filename category and the PSI subcategory "
            "(experiment/run label). These IDs are FlameLens-internal and must not be presented as "
            "PSI-issued dataset identifiers."
        ),
        "method": {
            "derivation": DATASET_DERIVATION,
            "top_level_category_rule": (
                "Text between the '<PSI-ID>_' prefix and the next underscore in the filename, "
                "e.g. 'Raw Data', 'Science Documents', 'Engineering Documents'."
            ),
            "subcategory_field": "PSI file object 'subcategory' (experiment/run label), empty when PSI omits it.",
            "subcategory_normalization": "trim, then collapse whitespace around '/' to a single '/'",
            "known_filename_anomalies": [
                "PSI-25 metadata archive filename contains 'PSI-101'",
                "PSI-101 contains a top-level label 'SAME' that is not a PSI category",
            ],
            "dataset_description_available": False,
            "psi_dataset_entity_exists": False,
        },
        "counts": {
            "total_datasets": len(datasets_sorted),
            "datasets_with_descriptions": 0,
            "per_investigation": {
                investigation_id: sum(
                    1 for dataset in datasets_sorted if dataset["investigation_id"] == investigation_id
                )
                for investigation_id in PILOT_IDS
            },
        },
        "datasets": datasets_sorted,
    }

    return files_inventory, datasets_inventory


def build_storage_summary(
    investigations: dict[str, Any],
    files_inventory: dict[str, Any],
    datasets_inventory: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    files = files_inventory["files"]
    by_investigation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in files:
        by_investigation[record["investigation_id"]].append(record)

    dataset_counts = datasets_inventory["counts"]["per_investigation"]
    investigation_rows: list[dict[str, Any]] = []
    investigation_lookup = {row["investigation_id"]: row for row in investigations["investigations"]}

    for investigation_id in PILOT_IDS:
        rows = by_investigation[investigation_id]
        payload = investigation_lookup[investigation_id]
        reported = payload["reported_total_file_size_bytes"]
        total = sum(record["size_bytes"] or 0 for record in rows)
        known = sum(1 for record in rows if record["size_known"])
        unknown = len(rows) - known
        over = [record for record in rows if record["download_status"] == "OVER_LIMIT"]
        eligible = [record for record in rows if record["download_eligible"]]
        formats = Counter(record["extension"] or "(none)" for record in rows)
        categories = Counter(record["format_category"] for record in rows)
        removed = [
            record
            for record in files_inventory["historical_removed_files"]
            if record["investigation_id"] == investigation_id
        ]
        delta = total - (reported or 0)
        # A materially incomplete listing is one where PSI's own reported total
        # exceeds the sum of the files the API exposes by more than 1 MiB.
        listing_complete = not (reported is not None and abs(delta) > 1024 * 1024 and total < reported)
        largest = sorted(rows, key=lambda record: -(record["size_bytes"] or 0))[:5]

        notes: list[str] = []
        if not listing_complete:
            notes.append(
                "PSI reports a total file size far larger than the sum of files exposed by the API; "
                "the file listing is incomplete."
            )
        if reported is not None and 0 < abs(delta) <= 1024 * 1024:
            notes.append(
                "Minor unexplained delta between summed file sizes and PSI's reported total "
                "(<= 1 MiB); no files appear to be missing."
            )
        if investigation_id == "PSI-99":
            notes.append(
                "Only the experimental table and a metadata archive are exposed, although the "
                "investigation text references a Science document folder that is not listed."
            )
        if investigation_id == "PSI-98":
            notes.append(
                "PSI reports the same start/end dates as PSI-102 (2001-03-02 to 2008-02-28), which "
                "conflicts with the 2016 Saffire-I flight described in the investigation text; "
                "treated as a PSI metadata anomaly."
            )
        if investigation_id == "PSI-102":
            notes.append(
                "Four analyzed-data XML files are reported with size 0 B; verify them during the "
                "download stage instead of assuming the files are valid."
            )

        investigation_rows.append(
            {
                "investigation_id": investigation_id,
                "title": payload["title"],
                "acronym": payload["acronym"],
                "dataset_count": dataset_counts.get(investigation_id, 0),
                "file_counts": {
                    "total_discovered": len(rows),
                    "known_remote_size": known,
                    "unknown_remote_size": unknown,
                    "downloaded": 0,
                    "pending_download": len(eligible),
                    "over_limit": len(over),
                    "zero_byte": sum(1 for record in rows if record["empty_file"]),
                    "failed_downloads": 0,
                    "restricted": sum(1 for record in rows if record["restricted"]),
                    "invisible": sum(1 for record in rows if not record["visible"]),
                },
                "storage": {
                    "remote_inventory_size_bytes": total,
                    "remote_inventory_size_human": human_bytes(total),
                    "remote_inventory_complete": listing_complete,
                    "remote_inventory_is_known_size_subtotal": not listing_complete,
                    "psi_reported_total_file_size_bytes": reported,
                    "psi_reported_total_file_size_human": human_bytes(reported),
                    "delta_vs_reported_bytes": delta if reported is not None else None,
                    "local_downloaded_size_bytes": 0,
                    "local_downloaded_size_human": "0 B",
                    "pending_download_size_bytes": sum(record["size_bytes"] or 0 for record in eligible),
                    "pending_download_size_human": human_bytes(
                        sum(record["size_bytes"] or 0 for record in eligible)
                    ),
                    "over_limit_size_bytes": sum(record["size_bytes"] or 0 for record in over),
                    "over_limit_size_human": human_bytes(sum(record["size_bytes"] or 0 for record in over)),
                    "unknown_size_file_count": unknown,
                },
                "format_distribution": dict(sorted(formats.items())),
                "format_category_distribution": dict(sorted(categories.items())),
                "largest_files": [
                    {
                        "file_id": record["file_id"],
                        "filename": record["filename"],
                        "size_bytes": record["size_bytes"],
                        "size_human": human_bytes(record["size_bytes"]),
                        "download_status": record["download_status"],
                    }
                    for record in largest
                ],
                "historical_removed": {
                    "file_count": len(removed),
                    "total_size_bytes": sum(record["size_bytes"] or 0 for record in removed),
                    "total_size_human": human_bytes(sum(record["size_bytes"] or 0 for record in removed)),
                },
                "notes": notes,
            }
        )

    uninventoried = [
        {
            "investigation_id": row["investigation_id"],
            "title": row["title"],
            "audit_level": row["audit_level"],
            "reported_total_file_size_bytes": row["reported_total_file_size_bytes"],
        }
        for row in investigations["investigations"]
        if not row["file_inventory_available"]
    ]

    current_total = files_inventory["counts"]["current_total_size_bytes"]
    reported_total = sum(
        row["storage"]["psi_reported_total_file_size_bytes"] or 0
        for row in investigation_rows
        if row["storage"]["psi_reported_total_file_size_bytes"] is not None
    )
    complete = all(row["storage"]["remote_inventory_complete"] for row in investigation_rows)

    all_formats = Counter()
    all_categories = Counter()
    for row in investigation_rows:
        all_formats.update(row["format_distribution"])
        all_categories.update(row["format_category_distribution"])

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": generated_at,
        "description": (
            "Storage analytics for the audited pilot investigations. Remote inventory size is the "
            "sum of file sizes PSI exposes through its API. Local downloaded size is always kept "
            "separate. No scientific data files have been downloaded at Stage 1."
        ),
        "units": {
            "byte_conversion": "binary: 1 KB = 1024 B, 1 MB = 1024^2 B, 1 GB = 1024^3 B, 1 TB = 1024^4 B",
            "size_fields_suffix": "_bytes",
        },
        "download_policy": files_inventory["download_policy"],
        "global": {
            "investigations_discovered": investigations["counts"]["total_investigations"],
            "investigations_with_file_inventory": investigations["counts"]["with_file_inventory"],
            "investigations_without_file_inventory": len(uninventoried),
            "dataset_groups": datasets_inventory["counts"]["total_datasets"],
            "file_counts": files_inventory["counts"],
            "remote_inventory_size_bytes": current_total,
            "remote_inventory_size_human": human_bytes(current_total),
            "psi_reported_total_file_size_bytes": reported_total,
            "psi_reported_total_file_size_human": human_bytes(reported_total),
            "delta_vs_reported_bytes": current_total - reported_total,
            "remote_inventory_complete": complete,
            "local_downloaded_size_bytes": 0,
            "local_downloaded_size_human": "0 B",
            "pending_download_file_count": files_inventory["counts"]["download_eligible_files"],
            "pending_download_size_bytes": sum(
                row["storage"]["pending_download_size_bytes"] for row in investigation_rows
            ),
            "pending_download_size_human": human_bytes(
                sum(row["storage"]["pending_download_size_bytes"] for row in investigation_rows)
            ),
            "over_limit_file_count": files_inventory["counts"]["over_limit_files"],
            "over_limit_size_bytes": sum(
                row["storage"]["over_limit_size_bytes"] for row in investigation_rows
            ),
            "over_limit_size_human": human_bytes(
                sum(row["storage"]["over_limit_size_bytes"] for row in investigation_rows)
            ),
            "unknown_size_file_count": files_inventory["counts"]["current_unknown_size_files"],
            "zero_byte_file_count": files_inventory["counts"]["zero_byte_files"],
            "format_distribution": dict(sorted(all_formats.items())),
            "format_category_distribution": dict(sorted(all_categories.items())),
        },
        "investigations": investigation_rows,
        "investigations_without_file_inventory": uninventoried,
        "data_gaps": [
            {
                "id": "GAP-001",
                "severity": "high",
                "investigation_id": "PSI-99",
                "summary": "API file listing is incomplete relative to PSI's own reported total file size.",
                "details": (
                    "totalFileSize is 16,931,016,137 B (~15.77 GiB), while the API exposes only an "
                    "experimental table (1,973 B) and metadata archive (10,539 B). 'added' and "
                    "'removed' arrays are empty. Raw data, videos and science documents are not listed."
                ),
                "recommended_action": (
                    "Manually inspect the PSI web UI for PSI-99, then re-query the API with an "
                    "authenticated session or report the gap to PSI."
                ),
            },
            {
                "id": "GAP-002",
                "severity": "medium",
                "investigation_id": "ALL",
                "summary": "PSI exposes no dataset entity or dataset-level descriptions.",
                "details": (
                    "Datasets in this audit are FlameLens-derived groups based on filename category "
                    "and PSI subcategory. They must not be presented as PSI-authored datasets."
                ),
                "recommended_action": (
                    "Carry the derivation flag into the Data Contract and label dataset groups as "
                    "derived in the UI and API."
                ),
            },
            {
                "id": "GAP-003",
                "severity": "medium",
                "investigation_id": "ALL",
                "summary": "Legacy per-file remote_url values are dead.",
                "details": (
                    "Most legacy URLs point to the retired psi.ndc.nasa.gov host (DNS failure); the "
                    "remaining relative /datamanager/file/... paths return HTTP 404. Files are only "
                    "retrievable through the /geode-py/ws/studies/{id}/download endpoint, which "
                    "returns a short-lived signed S3 URL."
                ),
                "recommended_action": (
                    "Use the download endpoint and request a fresh signed URL for every transfer; "
                    "never persist signed URLs."
                ),
            },
            {
                "id": "GAP-004",
                "severity": "low",
                "investigation_id": "PSI-98, PSI-100, PSI-101",
                "summary": "Small unexplained delta between summed file sizes and PSI totalFileSize.",
                "details": (
                    "Deltas are -242 B (PSI-98), -363 B (PSI-100) and -11,037 B (PSI-101), all far "
                    "below one file; treated as accounting noise rather than missing files."
                ),
                "recommended_action": "Record the delta in ingestion runs and monitor for growth.",
            },
            {
                "id": "GAP-005",
                "severity": "low",
                "investigation_id": "19 non-pilot investigations",
                "summary": "File/dataset inventory exists only for the 7 pilot investigations.",
                "details": "Nineteen combustion investigations have official descriptions but no file inventory yet.",
                "recommended_action": "Extend the Stage 4 ingestion pipeline to all 26 investigations.",
            },
            {
                "id": "GAP-006",
                "severity": "low",
                "investigation_id": "ALL",
                "summary": "No per-file descriptions are exposed by PSI.",
                "details": "File objects contain names, sizes, paths and timestamps but no description field.",
                "recommended_action": "Do not invent file descriptions; derive display labels from filenames only.",
            },
            {
                "id": "GAP-007",
                "severity": "medium",
                "investigation_id": "PSI-102",
                "summary": "Four current analyzed-data XML files are reported with size 0 B.",
                "details": (
                    "PSI-102_Analyzed Data_16937___9.xml, 16904___9.xml, 16942___9.xml and "
                    "16912___9.xml have file_size 0. Four historical 'removed' files also report 0 B. "
                    "A zero-byte size may be a PSI metadata placeholder or a genuinely empty file."
                ),
                "recommended_action": (
                    "During Stage 4, request Range: bytes=0-0 for each zero-byte file and record the "
                    "actual content length; never report a zero-byte download as a successful parse."
                ),
            },
            {
                "id": "GAP-008",
                "severity": "medium",
                "investigation_id": "PSI-98",
                "summary": "Investigation dates conflict with the described mission.",
                "details": (
                    "PSI-98 (Saffire-I) reports start 2001-03-02 and end 2008-02-28, identical to "
                    "PSI-102 (SAME), while its description refers to the 2016 Cygnus flight. PSI-100 "
                    "also has no end date."
                ),
                "recommended_action": (
                    "Preserve the PSI-reported values verbatim, flag them as unverified, and do not use "
                    "them for chronological comparisons without manual confirmation."
                ),
            },
            {
                "id": "GAP-009",
                "severity": "low",
                "investigation_id": "PSI-25, PSI-101",
                "summary": "Filename inconsistencies distort derived category labels.",
                "details": (
                    "The PSI-25 metadata archive filename references 'PSI-101', and PSI-101 contains a "
                    "file whose top-level label is 'SAME'. Derived datasets are therefore grouped by "
                    "filename convention, not by a PSI-issued category."
                ),
                "recommended_action": (
                    "Keep the derivation flag on every dataset and allow manual dataset corrections in "
                    "the Data Contract without mutating raw PSI metadata."
                ),
            },
        ],
    }


# ---------------------------------------------------------------------------
# Writing and verification
# ---------------------------------------------------------------------------


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def verify(
    investigations: dict[str, Any],
    datasets: dict[str, Any],
    files: dict[str, Any],
    storage: dict[str, Any],
) -> list[str]:
    problems: list[str] = []

    file_ids = [record["file_id"] for record in files["files"]]
    if len(file_ids) != len(set(file_ids)):
        problems.append("Duplicate file_id values in files_inventory.json")

    dataset_ids = [record["dataset_id"] for record in datasets["datasets"]]
    if len(dataset_ids) != len(set(dataset_ids)):
        problems.append("Duplicate dataset_id values in datasets_inventory.json")

    assigned = [file_id for dataset in datasets["datasets"] for file_id in dataset["file_ids"]]
    if sorted(assigned) != sorted(file_ids):
        problems.append("Dataset file_ids do not exactly cover the current file inventory")

    if sum(dataset["file_count"] for dataset in datasets["datasets"]) != len(files["files"]):
        problems.append("Dataset file_count total does not match the current file count")

    for dataset in datasets["datasets"]:
        if dataset["known_size_file_count"] != len(dataset["file_ids"]):
            problems.append(f"Dataset {dataset['dataset_id']} has unknown-size files")
        if dataset["total_size_bytes"] <= 0:
            problems.append(f"Dataset {dataset['dataset_id']} has non-positive size")

    current_total = sum(record["size_bytes"] or 0 for record in files["files"])
    if current_total != files["counts"]["current_total_size_bytes"]:
        problems.append("files_inventory totals do not reconcile")
    if current_total != storage["global"]["remote_inventory_size_bytes"]:
        problems.append("storage_summary global total does not reconcile with files_inventory")

    for row in storage["investigations"]:
        if row["storage"]["remote_inventory_size_bytes"] != sum(
            record["size_bytes"] or 0
            for record in files["files"]
            if record["investigation_id"] == row["investigation_id"]
        ):
            problems.append(f"Storage row mismatch for {row['investigation_id']}")
        if row["file_counts"]["total_discovered"] != sum(
            1 for record in files["files"] if record["investigation_id"] == row["investigation_id"]
        ):
            problems.append(f"File count mismatch for {row['investigation_id']}")

    # Every current file must be either eligible or explicitly over limit.
    for record in files["files"]:
        if record["download_status"] not in {"PENDING", "OVER_LIMIT"}:
            problems.append(f"Unexpected download status for {record['file_id']}: {record['download_status']}")
        if record["download_eligible"] and record["download_status"] != "PENDING":
            problems.append(f"Eligible file not marked PENDING: {record['file_id']}")
        if record["download_status"] == "OVER_LIMIT" and record["size_bytes"] <= MAX_FILE_SIZE_BYTES:
            problems.append(f"Over-limit file within limit: {record['file_id']}")

    if investigations["counts"]["total_investigations"] != len(investigations["investigations"]):
        problems.append("Investigation count does not reconcile")
    if investigations["counts"]["with_file_inventory"] != len(storage["investigations"]):
        problems.append("Investigation/file-inventory count mismatch")

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify reconciliation after writing")
    args = parser.parse_args(argv)

    generated_at = now_utc()
    manifest = load_manifest()
    search = load_search_snapshot()
    pilots = load_pilot_payloads()
    descriptions, description_counts = load_descriptions()

    investigations = build_investigations(
        search, pilots, descriptions, description_counts, generated_at
    )
    investigations["source"]["snapshot_captured_at_utc"] = manifest.get("captured_at_utc")

    files_inventory, datasets_inventory = build_files_and_datasets(pilots, generated_at)
    storage = build_storage_summary(
        investigations, files_inventory, datasets_inventory, generated_at
    )

    write_json(METADATA_DIR / "investigations_inventory.json", investigations)
    write_json(METADATA_DIR / "files_inventory.json", files_inventory)
    write_json(METADATA_DIR / "datasets_inventory.json", datasets_inventory)
    write_json(METADATA_DIR / "storage_summary.json", storage)

    global_row = storage["global"]
    print("PSI Stage 1 audit inventories written")
    print(f"  investigations: {investigations['counts']['total_investigations']} "
          f"(full audit: {investigations['counts']['full_audit']}, "
          f"description only: {investigations['counts']['description_only']})")
    print(f"  datasets:       {datasets_inventory['counts']['total_datasets']}")
    print(f"  current files:  {global_row['file_counts']['current_files']} "
          f"({global_row['remote_inventory_size_human']})")
    print(f"  over limit:     {global_row['over_limit_file_count']} "
          f"({global_row['over_limit_size_human']})")
    print(f"  eligible:       {global_row['pending_download_file_count']} "
          f"({global_row['pending_download_size_human']})")
    print(f"  complete:      {global_row['remote_inventory_complete']}")
    print()
    print("Per investigation:")
    print(f"  {'ID':8s} {'files':>6s} {'datasets':>8s} {'remote size':>12s} {'over':>5s} {'eligible':>8s}")
    for row in storage["investigations"]:
        print(
            f"  {row['investigation_id']:8s} "
            f"{row['file_counts']['total_discovered']:6d} "
            f"{row['dataset_count']:8d} "
            f"{row['storage']['remote_inventory_size_human']:>12s} "
            f"{row['file_counts']['over_limit']:5d} "
            f"{row['file_counts']['pending_download']:8d}"
        )

    if args.check:
        problems = verify(investigations, datasets_inventory, files_inventory, storage)
        if problems:
            print("\nRECONCILIATION FAILED", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            return 1
        print("\nReconciliation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Investigation, file and storage endpoints."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response

from app.schemas.dataset import DatasetListResponse
from app.schemas.investigation import (
    FileListResponse,
    InvestigationDetail,
    InvestigationListResponse,
    StorageSummaryResponse,
)
from app.services import investigation_service as service

router = APIRouter()


def _csv_response(filename: str, rows: list[dict]) -> Response:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(service.EXPORT_COLUMNS))
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _json_response(filename: str, payload: dict) -> Response:
    return Response(
        content=json.dumps(payload, indent=2, default=str),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/investigations",
    response_model=InvestigationListResponse,
    summary="List and search investigations",
)
async def list_investigations(
    q: str | None = Query(None, description="Free-text search over ID, title, keywords, descriptions"),
    research_area: str | None = None,
    sub_research_area: str | None = None,
    flight_platform: str | None = None,
    audit_level: str | None = None,
    has_file_inventory: bool | None = None,
    sort_by: Literal["id", "title", "start_date", "end_date", "file_count", "remote_size"] = "id",
    order: Literal["asc", "desc"] = "asc",
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
):
    """Paginated investigation search over the Stage 1 NASA PSI inventory."""
    return service.list_investigations(
        query=q,
        research_area=research_area,
        sub_research_area=sub_research_area,
        flight_platform=flight_platform,
        audit_level=audit_level,
        has_file_inventory=has_file_inventory,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/investigations/{investigation_id}",
    response_model=InvestigationDetail,
    summary="Investigation detail",
)
async def get_investigation(investigation_id: str):
    """Full preserved NASA PSI record plus derived inventory analytics."""
    return service.get_investigation_detail(investigation_id)


@router.get(
    "/investigations/{investigation_id}/files",
    response_model=FileListResponse,
    summary="Files for an investigation",
)
async def list_investigation_files(
    investigation_id: str,
    q: str | None = None,
    extension: str | None = None,
    format_category: str | None = None,
    download_status: str | None = None,
    dataset_id: str | None = None,
    min_size: int | None = Query(None, ge=0),
    max_size: int | None = Query(None, ge=0),
    sort_by: Literal["filename", "size", "extension", "dataset", "investigation"] = "filename",
    order: Literal["asc", "desc"] = "asc",
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    return service.list_files(
        investigation_id=investigation_id,
        query=q,
        extension=extension,
        format_category=format_category,
        download_status=download_status,
        dataset_id=dataset_id,
        min_size=min_size,
        max_size=max_size,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/investigations/{investigation_id}/storage-summary",
    response_model=StorageSummaryResponse,
    summary="Storage summary for an investigation",
)
async def get_storage_summary(investigation_id: str):
    """Remote inventory size, local storage (always separate), and status counts."""
    return service.get_storage_summary(investigation_id)


@router.get(
    "/investigations/{investigation_id}/datasets",
    response_model=DatasetListResponse,
    summary="Derived file groups for an investigation",
)
async def get_datasets(investigation_id: str):
    return service.get_datasets(investigation_id)


@router.get(
    "/investigations/{investigation_id}/files/export",
    summary="Export investigation file inventory as CSV or JSON",
)
async def export_investigation_files(
    investigation_id: str,
    format: Literal["csv", "json"] = Query("csv"),
    q: str | None = None,
    extension: str | None = None,
    format_category: str | None = None,
    download_status: str | None = None,
    dataset_id: str | None = None,
    sort_by: Literal["filename", "size", "extension", "dataset", "investigation"] = "filename",
    order: Literal["asc", "desc"] = "asc",
):
    rows = service.list_export_files(
        investigation_id=investigation_id,
        query=q,
        extension=extension,
        format_category=format_category,
        download_status=download_status,
        dataset_id=dataset_id,
        sort_by=sort_by,
        order=order,
    )
    export_rows = service.export_rows(rows)
    stem = f"flamelens_{investigation_id.upper()}_files"
    if format == "json":
        return _json_response(
            f"{stem}.json",
            {
                "investigation_id": investigation_id.upper(),
                "exported_at_utc": service.store.investigations_payload.get("generated_at_utc"),
                "record_count": len(export_rows),
                "records": export_rows,
            },
        )
    return _csv_response(f"{stem}.csv", export_rows)

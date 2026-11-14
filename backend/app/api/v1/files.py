"""Global file inventory endpoints across all investigations."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.schemas.investigation import FileListResponse
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


@router.get("/files", response_model=FileListResponse, summary="Search the global file inventory")
async def list_files(
    q: str | None = None,
    investigation_id: str | None = None,
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


@router.get("/files/export", summary="Export the global file inventory as CSV or JSON")
async def export_files(
    format: Literal["csv", "json"] = Query("csv"),
    q: str | None = None,
    investigation_id: str | None = None,
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
    stem = "flamelens_files"
    if investigation_id:
        stem = f"flamelens_{investigation_id.upper()}_files"
    if format == "json":
        return Response(
            content=json.dumps(
                {
                    "investigation_id": investigation_id.upper() if investigation_id else None,
                    "exported_at_utc": service.store.investigations_payload.get("generated_at_utc"),
                    "record_count": len(export_rows),
                    "records": export_rows,
                },
                indent=2,
                default=str,
            ),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{stem}.json"'},
        )
    return _csv_response(f"{stem}.csv", export_rows)

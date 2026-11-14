"""Two-investigation metadata and file-inventory comparison."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas.comparison import ComparisonResponse
from app.services import comparison_service

router = APIRouter()


@router.get(
    "/comparison",
    response_model=ComparisonResponse,
    summary="Compare metadata and file inventories for two investigations",
)
async def compare(
    ids: str = Query(
        ...,
        description="Comma-separated pair of investigation IDs, e.g. PSI-22,PSI-25",
    )
):
    return comparison_service.compare(ids.split(","))

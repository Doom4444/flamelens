"""Dataset-group listing endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.dataset import DatasetListResponse
from app.services import dataset_service

router = APIRouter()


@router.get("/datasets", response_model=DatasetListResponse, summary="List derived file groups")
async def list_datasets():
    """FlameLens-derived groups, not NASA PSI dataset entities."""
    return dataset_service.list_datasets()

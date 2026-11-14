"""Dashboard and storage analytics endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.services import analytics_service

router = APIRouter()


@router.get("/analytics/overview", summary="Dashboard overview statistics")
async def overview():
    """Every value is computed from the Stage 1 NASA PSI inventories."""
    return analytics_service.overview()


@router.get("/analytics/storage", summary="Storage analytics")
async def storage():
    return analytics_service.storage_analytics()

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.config import Settings, get_settings

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Returns system health status and basic application metadata.
    """
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

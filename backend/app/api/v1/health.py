from fastapi import APIRouter

from app.config import APP_NAME, APP_VERSION

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
    }
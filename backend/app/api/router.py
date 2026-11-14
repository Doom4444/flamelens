from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.chatbot import router as chatbot_router
from app.api.v1.comparison import router as comparison_router
from app.api.v1.datasets import router as datasets_router
from app.api.v1.files import router as files_router
from app.api.v1.health import router as health_router
from app.api.v1.investigations import router as investigations_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(analytics_router, tags=["Analytics"])
api_router.include_router(investigations_router, tags=["Investigations"])
api_router.include_router(files_router, tags=["Files"])
api_router.include_router(datasets_router, tags=["Datasets"])
api_router.include_router(comparison_router, tags=["Comparison"])
api_router.include_router(chatbot_router, tags=["Assistant"])

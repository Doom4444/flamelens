"""Metadata-grounded assistant endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.chatbot import AssistantQuery, AssistantResponse
from app.services import assistant_service

router = APIRouter()


@router.post(
    "/assistant/query",
    response_model=AssistantResponse,
    summary="Ask a question over investigation metadata",
)
async def query(payload: AssistantQuery):
    return assistant_service.answer(payload.query, limit=payload.limit)

"""Assistant request/response models for metadata-grounded retrieval."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AssistantQuery(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=4, ge=1, le=10)


class Citation(BaseModel):
    investigation_id: str
    title: str
    field: str
    snippet: str
    score: float
    matched_terms: list[str] = Field(default_factory=list)


class AssistantResponse(BaseModel):
    query: str
    answer: str
    answer_type: str = "metadata_retrieval"
    provider: str = "metadata-retrieval"
    citations: list[Citation] = Field(default_factory=list)
    disclaimers: list[str] = Field(default_factory=list)
    generated_at_utc: str

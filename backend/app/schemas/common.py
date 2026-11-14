"""Shared response models for the metadata API."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=1)
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    pagination: PaginationMeta


class ProvenanceInfo(BaseModel):
    """Where a response's numbers came from, kept explicit for integrity."""

    model_config = ConfigDict(extra="allow")

    source: str = "NASA PSI Stage 1 audit inventories"
    inventory_generated_at_utc: str | None = None
    snapshot_captured_at_utc: str | None = None
    local_storage_note: str = (
        "Local downloaded size is tracked separately from remote inventory size. "
        "No scientific files are downloaded in this prototype."
    )

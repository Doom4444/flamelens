"""Dataset-group response models.

NASA PSI does not expose dataset entities. Every group is derived from the
top-level filename category plus the PSI subcategory, and the derivation is
carried on the model so the API can never imply otherwise.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DatasetGroup(BaseModel):
    model_config = ConfigDict(extra="allow")

    dataset_id: str
    investigation_id: str
    name: str
    top_level_category: str | None = None
    psi_subcategory: str | None = None
    description: str | None = None
    description_available: bool = False
    derivation: str = "top_level_filename_category + psi_subcategory"
    file_count: int = 0
    known_size_file_count: int = 0
    total_size_bytes: int = 0
    format_distribution: dict[str, int] = Field(default_factory=dict)
    file_ids: list[str] = Field(default_factory=list)


class DatasetListResponse(BaseModel):
    investigation_id: str | None = None
    items: list[DatasetGroup]
    total_items: int
    total_size_bytes: int
    method: dict[str, Any] = Field(default_factory=dict)

"""Comparison response models.

The comparison is explicitly limited to metadata and file-inventory data.
No experimental measurement comparison is performed because no parsed
measurement datasets are integrated yet.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.investigation import StorageMetrics


class ComparedInvestigation(BaseModel):
    model_config = ConfigDict(extra="allow")

    investigation_id: str
    title: str
    acronym: str | None = None
    research_area: str | None = None
    sub_research_area: str | None = None
    project_type: str | None = None
    flight_platform: str | None = None
    experiment_hardware: dict[str, Any] | None = None
    managing_nasa_center: str | None = None
    sponsoring_agency: str | None = None
    start_date_iso: str | None = None
    end_date_iso: str | None = None
    doi: str | None = None
    keywords: list[str] = Field(default_factory=list)
    related_investigations: list[str] = Field(default_factory=list)
    objectives: str | None = None
    approach: str | None = None
    hypothesis: str | None = None
    research_impacts: str | None = None
    file_count: int = 0
    dataset_count: int = 0
    storage: StorageMetrics | None = None
    format_distribution: dict[str, int] = Field(default_factory=dict)
    format_category_distribution: dict[str, int] = Field(default_factory=dict)
    file_inventory_available: bool = False


class ComparisonResponse(BaseModel):
    comparison_scope: str = "metadata_and_file_inventory"
    measurement_comparison_available: bool = False
    notice: str = (
        "This comparison covers NASA PSI metadata and file inventory only. "
        "No experimental measurements are parsed or compared, and no scientific "
        "comparability between investigations is implied."
    )
    investigations: list[ComparedInvestigation]
    shared_keywords: list[str] = Field(default_factory=list)
    shared_formats: list[str] = Field(default_factory=list)
    format_overlap: dict[str, dict[str, int]] = Field(default_factory=dict)
    inventory_deltas: dict[str, Any] = Field(default_factory=dict)

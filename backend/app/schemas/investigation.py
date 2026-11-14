"""Investigation, file and storage response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PaginationMeta
from app.schemas.dataset import DatasetGroup


class DescriptionBlock(BaseModel):
    objectives: str | None = None
    approach: str | None = None
    hypothesis: str | None = None
    research_impacts: str | None = None


class StorageMetrics(BaseModel):
    model_config = ConfigDict(extra="allow")

    remote_inventory_size_bytes: int = 0
    remote_inventory_size_human: str | None = None
    remote_inventory_complete: bool = True
    remote_inventory_is_known_size_subtotal: bool = False
    psi_reported_total_file_size_bytes: int | None = None
    psi_reported_total_file_size_human: str | None = None
    delta_vs_reported_bytes: int | None = None
    local_downloaded_size_bytes: int = 0
    local_downloaded_size_human: str = "0 B"
    pending_download_size_bytes: int = 0
    pending_download_size_human: str | None = None
    over_limit_size_bytes: int = 0
    over_limit_size_human: str | None = None
    unknown_size_file_count: int = 0


class FileRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    file_id: str
    investigation_id: str
    dataset_id: str | None = None
    dataset_name: str | None = None
    lifecycle_status: str = "current"
    filename: str
    extension: str | None = None
    mime_type: str | None = None
    format_category: str | None = None
    psi_subcategory: str | None = None
    description: str | None = None
    description_available: bool = False
    source_fields: list[str] = Field(default_factory=list)
    remote_path: str | None = None
    s3_path: str | None = None
    bucket: str | None = None
    psi_file_version: int | None = None
    size_bytes: int | None = None
    size_known: bool = True
    empty_file: bool = False
    download_url: str | None = None
    download_url_requires_signed_redirect: bool = True
    legacy_remote_url: str | None = None
    legacy_url_status: str | None = None
    download_eligible: bool = False
    download_status: str = "PENDING"
    manual_approval_required: bool = False
    downloaded: bool = False
    local_size_bytes: int | None = None
    local_path: str | None = None
    sha256: str | None = None
    parsing_status: str = "NOT_PARSED"
    restricted: bool = False
    visible: bool = True
    psi_created_at_utc: str | None = None
    psi_modified_at_utc: str | None = None
    discovered_at_utc: str | None = None


class InvestigationSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    investigation_id: str
    title: str
    acronym: str | None = None
    research_area: str | None = None
    sub_research_area: str | None = None
    project_type: str | None = None
    flight_platform: str | None = None
    start_date_iso: str | None = None
    end_date_iso: str | None = None
    doi: str | None = None
    keywords: list[str] = Field(default_factory=list)
    description: DescriptionBlock = Field(default_factory=DescriptionBlock)
    audit_level: str = "description_only"
    file_inventory_available: bool = False
    dataset_count: int = 0
    file_count: int = 0
    file_counts: dict[str, Any] = Field(default_factory=dict)
    storage: StorageMetrics | None = None


class InvestigationDetail(InvestigationSummary):
    experiment_hardware: dict[str, Any] | None = None
    managing_nasa_center: str | None = None
    sponsoring_agency: str | None = None
    proposal_title: str | None = None
    related_investigations: list[str] = Field(default_factory=list)
    contacts: list[dict[str, Any]] = Field(default_factory=list)
    publications: list[dict[str, Any]] = Field(default_factory=list)
    publication_titles_structured: bool = False
    publication_titles_raw: str | None = None
    publication_authors_raw: str | None = None
    field_presence: dict[str, bool] = Field(default_factory=dict)
    psi_api_url: str | None = None
    data_source: str | None = None
    psi_version: int | None = None
    reported_total_file_size_bytes: int | None = None
    reported_total_file_size_human: str | None = None
    snapshot_sha256: str | None = None
    existing_project_metadata: dict[str, Any] = Field(default_factory=dict)
    format_distribution: dict[str, int] = Field(default_factory=dict)
    format_category_distribution: dict[str, int] = Field(default_factory=dict)
    historical_removed: dict[str, Any] = Field(default_factory=dict)
    storage_notes: list[str] = Field(default_factory=list)
    dataset_groups: list[DatasetGroup] = Field(default_factory=list)
    related_edges: list[dict[str, str]] = Field(default_factory=list)
    data_gaps: list[dict[str, Any]] = Field(default_factory=list)


class InvestigationListResponse(BaseModel):
    items: list[InvestigationSummary]
    pagination: PaginationMeta
    filters: dict[str, Any] = Field(default_factory=dict)
    facets: dict[str, list[str]] = Field(default_factory=dict)
    generated_at_utc: str | None = None


class FileListResponse(BaseModel):
    items: list[FileRecord]
    pagination: PaginationMeta
    filters: dict[str, Any] = Field(default_factory=dict)
    totals: dict[str, Any] = Field(default_factory=dict)


class StorageSummaryResponse(BaseModel):
    investigation_id: str
    title: str | None = None
    acronym: str | None = None
    dataset_count: int = 0
    file_counts: dict[str, Any] = Field(default_factory=dict)
    storage: StorageMetrics
    format_distribution: dict[str, int] = Field(default_factory=dict)
    format_category_distribution: dict[str, int] = Field(default_factory=dict)
    historical_removed: dict[str, Any] = Field(default_factory=dict)
    largest_files: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    data_gaps: list[dict[str, Any]] = Field(default_factory=list)

export type ConnectionStatus = 'connected' | 'disconnected' | 'checking';

export interface BackendHealthResponse {
  status: string;
  application: string;
  version: string;
  environment: string;
  timestamp: string;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface DescriptionBlock {
  objectives?: string | null;
  approach?: string | null;
  hypothesis?: string | null;
  research_impacts?: string | null;
}

export interface StorageMetrics {
  remote_inventory_size_bytes: number;
  remote_inventory_size_human?: string | null;
  remote_inventory_complete: boolean;
  remote_inventory_is_known_size_subtotal: boolean;
  psi_reported_total_file_size_bytes?: number | null;
  psi_reported_total_file_size_human?: string | null;
  delta_vs_reported_bytes?: number | null;
  local_downloaded_size_bytes: number;
  local_downloaded_size_human?: string | null;
  pending_download_size_bytes: number;
  pending_download_size_human?: string | null;
  over_limit_size_bytes: number;
  over_limit_size_human?: string | null;
  unknown_size_file_count: number;
}

export type FileCounts = Record<string, number>;

export interface DatasetGroup {
  dataset_id: string;
  investigation_id: string;
  name: string;
  top_level_category?: string | null;
  psi_subcategory?: string | null;
  description?: string | null;
  description_available: boolean;
  derivation: string;
  file_count: number;
  known_size_file_count: number;
  total_size_bytes: number;
  format_distribution: Record<string, number>;
  file_ids: string[];
}

export interface InvestigationSummary {
  investigation_id: string;
  title: string;
  acronym?: string | null;
  research_area?: string | null;
  sub_research_area?: string | null;
  project_type?: string | null;
  flight_platform?: string | null;
  start_date_iso?: string | null;
  end_date_iso?: string | null;
  doi?: string | null;
  keywords: string[];
  description: DescriptionBlock;
  audit_level: string;
  file_inventory_available: boolean;
  dataset_count: number;
  file_count: number;
  file_counts: FileCounts;
  storage?: StorageMetrics | null;
}

export interface InvestigationDetail extends InvestigationSummary {
  experiment_hardware?: { name?: string | null; link?: string | null } | null;
  managing_nasa_center?: string | null;
  sponsoring_agency?: string | null;
  proposal_title?: string | null;
  related_investigations: string[];
  contacts: Array<Record<string, unknown>>;
  publications: Array<Record<string, unknown>>;
  field_presence: Record<string, boolean>;
  psi_api_url?: string | null;
  data_source?: string | null;
  psi_version?: number | null;
  reported_total_file_size_bytes?: number | null;
  reported_total_file_size_human?: string | null;
  snapshot_sha256?: string | null;
  existing_project_metadata: Record<string, unknown>;
  format_distribution: Record<string, number>;
  format_category_distribution: Record<string, number>;
  historical_removed: Record<string, unknown>;
  storage_notes: string[];
  dataset_groups: DatasetGroup[];
  related_edges: Array<Record<string, string>>;
  data_gaps: DataGap[];
}

export interface DataGap {
  id: string;
  severity: string;
  investigation_id: string;
  summary: string;
  details: string;
  recommended_action: string;
}

export interface FileRecord {
  file_id: string;
  investigation_id: string;
  dataset_id?: string | null;
  dataset_name?: string | null;
  lifecycle_status: string;
  filename: string;
  extension?: string | null;
  mime_type?: string | null;
  format_category?: string | null;
  psi_subcategory?: string | null;
  description?: string | null;
  remote_path?: string | null;
  s3_path?: string | null;
  bucket?: string | null;
  psi_file_version?: number | null;
  size_bytes?: number | null;
  size_known: boolean;
  empty_file: boolean;
  download_url?: string | null;
  download_url_requires_signed_redirect: boolean;
  legacy_remote_url?: string | null;
  legacy_url_status?: string | null;
  download_eligible: boolean;
  download_status: string;
  manual_approval_required: boolean;
  downloaded: boolean;
  local_size_bytes?: number | null;
  local_path?: string | null;
  sha256?: string | null;
  parsing_status: string;
  restricted: boolean;
  visible: boolean;
  psi_created_at_utc?: string | null;
  psi_modified_at_utc?: string | null;
  discovered_at_utc?: string | null;
}

export interface InvestigationFilters {
  q?: string | null;
  research_area?: string | null;
  sub_research_area?: string | null;
  flight_platform?: string | null;
  audit_level?: string | null;
  has_file_inventory?: boolean | null;
  sort_by?: string;
  order?: string;
}

export interface InvestigationFacets {
  research_areas: string[];
  sub_research_areas: string[];
  flight_platforms: string[];
}

export interface InvestigationListResponse {
  items: InvestigationSummary[];
  pagination: PaginationMeta;
  filters: InvestigationFilters;
  facets: InvestigationFacets;
  generated_at_utc?: string | null;
}

export interface FileTotals {
  total_items: number;
  known_size_items: number;
  unknown_size_items: number;
  remote_size_bytes: number;
  remote_size_human: string;
  local_downloaded_size_bytes: number;
  local_downloaded_size_human: string;
  downloaded_items: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  by_extension: Record<string, number>;
}

export interface FileListResponse {
  items: FileRecord[];
  pagination: PaginationMeta;
  filters: Record<string, unknown>;
  totals: FileTotals;
}

export interface StorageSummaryResponse {
  investigation_id: string;
  title?: string | null;
  acronym?: string | null;
  dataset_count: number;
  file_counts: FileCounts;
  storage: StorageMetrics;
  format_distribution: Record<string, number>;
  format_category_distribution: Record<string, number>;
  historical_removed: Record<string, unknown>;
  largest_files: FileRecord[];
  notes: string[];
  data_gaps: DataGap[];
}

export interface DatasetListResponse {
  investigation_id?: string | null;
  items: DatasetGroup[];
  total_items: number;
  total_size_bytes: number;
  per_investigation?: Record<string, number>;
  method: Record<string, unknown>;
}

export interface FileTypeStat {
  extension: string;
  format_category: string;
  count: number;
  size_bytes: number;
  size_human?: string | null;
  share_of_bytes: number;
}

export interface FormatCategoryStat {
  format_category: string;
  count: number;
  size_bytes: number;
  size_human?: string | null;
  share_of_bytes: number;
}

export interface DownloadStatusStat {
  download_status: string;
  count: number;
  size_bytes: number;
  size_human?: string | null;
}

export interface ResearchAreaStat {
  research_area: string;
  investigation_count: number;
  with_file_inventory: number;
}

export interface OverviewTotals {
  investigations: number;
  investigations_with_file_inventory: number;
  investigations_without_file_inventory: number;
  dataset_groups: number;
  files: number;
  remote_inventory_size_bytes: number;
  remote_inventory_size_human?: string | null;
  psi_reported_total_file_size_bytes?: number | null;
  psi_reported_total_file_size_human?: string | null;
  delta_vs_reported_bytes?: number | null;
  local_downloaded_size_bytes: number;
  local_downloaded_size_human?: string | null;
  downloaded_files: number;
  download_eligible_files: number;
  over_limit_files: number;
  zero_byte_files: number;
  historical_removed_files: number;
  data_gap_count: number;
}

export interface OverviewResponse {
  generated_at_utc?: string | null;
  snapshot_captured_at_utc?: string | null;
  data_source: string;
  totals: OverviewTotals;
  file_type_distribution: FileTypeStat[];
  format_category_distribution: FormatCategoryStat[];
  download_status_distribution: DownloadStatusStat[];
  research_area_distribution: ResearchAreaStat[];
  featured_investigations: InvestigationSummary[];
  download_policy: Record<string, unknown>;
  data_notes: string[];
}

export interface StorageRow {
  investigation_id: string;
  title: string;
  acronym?: string | null;
  dataset_count: number;
  file_counts: FileCounts;
  storage: StorageMetrics & { share_of_remote_bytes?: number };
  format_distribution: Record<string, number>;
  format_category_distribution: Record<string, number>;
  largest_files: Array<Record<string, unknown>>;
  historical_removed: Record<string, unknown>;
  notes: string[];
}

export interface StorageAnalyticsResponse {
  generated_at_utc?: string | null;
  snapshot_captured_at_utc?: string | null;
  global: StorageMetrics & {
    investigations_discovered: number;
    investigations_with_file_inventory: number;
    investigations_without_file_inventory: number;
    dataset_groups: number;
    file_counts: FileCounts;
    pending_download_file_count: number;
    over_limit_file_count: number;
    zero_byte_file_count: number;
    format_distribution: Record<string, number>;
    format_category_distribution: Record<string, number>;
    [key: string]: unknown;
  };
  investigations: StorageRow[];
  investigations_without_file_inventory: Array<{
    investigation_id: string;
    title: string;
    audit_level: string;
    reported_total_file_size_bytes?: number | null;
  }>;
  file_type_distribution: FileTypeStat[];
  format_category_distribution: FormatCategoryStat[];
  download_policy: Record<string, unknown>;
  data_gaps: DataGap[];
  units: Record<string, string>;
}

export interface ComparedInvestigation {
  investigation_id: string;
  title: string;
  acronym?: string | null;
  research_area?: string | null;
  sub_research_area?: string | null;
  project_type?: string | null;
  flight_platform?: string | null;
  experiment_hardware?: { name?: string | null } | null;
  managing_nasa_center?: string | null;
  sponsoring_agency?: string | null;
  start_date_iso?: string | null;
  end_date_iso?: string | null;
  doi?: string | null;
  keywords: string[];
  related_investigations: string[];
  objectives?: string | null;
  approach?: string | null;
  hypothesis?: string | null;
  research_impacts?: string | null;
  file_count: number;
  dataset_count: number;
  storage?: StorageMetrics | null;
  format_distribution: Record<string, number>;
  format_category_distribution: Record<string, number>;
  file_inventory_available: boolean;
}

export interface ComparisonResponse {
  comparison_scope: string;
  measurement_comparison_available: boolean;
  notice: string;
  investigations: ComparedInvestigation[];
  shared_keywords: string[];
  shared_formats: string[];
  format_overlap: Record<string, Record<string, number>>;
  inventory_deltas: Record<string, { difference: number; left: number; right: number }>;
}

export interface AssistantCitation {
  investigation_id: string;
  title: string;
  field: string;
  snippet: string;
  score: number;
  matched_terms: string[];
}

export interface AssistantResponse {
  query: string;
  answer: string;
  answer_type: string;
  provider: string;
  citations: AssistantCitation[];
  disclaimers: string[];
  generated_at_utc: string;
}

/* Legacy display types retained for the unused illustrative category card. */
export type ResearchCategoryType = 'prevention' | 'detection' | 'suppression';

export interface CategoryInfo {
  id: ResearchCategoryType;
  title: string;
  subtitle: string;
  description: string;
  exampleInvestigations: string[];
  focusAreas: string[];
  accentColor: string;
}

export interface InvestigationPreview {
  id: string;
  accessionId?: string;
  title: string;
  category: ResearchCategoryType;
  description: string;
  facility?: string;
  isIllustrative?: boolean;
}

export interface DashboardMetric {
  id: string;
  label: string;
  value: string | number;
  statusLabel: string;
  description: string;
  isPending: boolean;
}

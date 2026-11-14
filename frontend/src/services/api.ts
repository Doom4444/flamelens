import {
  AssistantResponse,
  ComparisonResponse,
  DatasetListResponse,
  FileListResponse,
  InvestigationDetail,
  InvestigationListResponse,
  OverviewResponse,
  StorageAnalyticsResponse,
  StorageSummaryResponse,
  BackendHealthResponse,
} from '../types';

/**
 * Backend origin.
 *
 * Production/staging builds must provide VITE_API_BASE_URL at build time. The
 * localhost fallback is only used by the Vite dev server so a missing variable
 * can never silently point a deployed site at the visitor's own machine.
 */
const configuredApiBase = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim();

export const API_BASE_URL: string = (
  configuredApiBase || (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')
).replace(/\/+$/, '');

export const isApiConfigured: boolean = API_BASE_URL.length > 0;

const API_PREFIX = '/api/v1';

const MISSING_API_BASE_MESSAGE =
  'Backend API URL is not configured. Set VITE_API_BASE_URL to the deployed backend origin (for example https://your-api.onrender.com) and rebuild the frontend.';

function apiUrl(path: string, query?: Record<string, QueryValue>): string {
  if (!isApiConfigured) {
    throw new ApiError(MISSING_API_BASE_MESSAGE);
  }
  return `${API_BASE_URL}${API_PREFIX}${path}${buildQuery(query)}`;
}

export class ApiError extends Error {
  status?: number;
  data?: unknown;

  constructor(message: string, status?: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

type QueryValue = string | number | boolean | null | undefined;

export function buildQuery(params?: Record<string, QueryValue>): string {
  const search = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined || value === null || value === '') return;
      search.set(key, String(value));
    });
  }
  const query = search.toString();
  return query ? `?${query}` : '';
}

async function request<T>(path: string, params?: Record<string, QueryValue>): Promise<T> {
  const url = apiUrl(path, params);
  let response: Response;
  try {
    response = await fetch(url, {
      headers: { Accept: 'application/json' },
    });
  } catch {
    throw new ApiError(
      `Cannot reach the FlameLens backend at ${API_BASE_URL}. Check that the API is running and that CORS_ORIGINS allows this site.`
    );
  }

  if (!response.ok) {
    let message = `Request failed with HTTP ${response.status}`;
    let payload: unknown = null;
    try {
      payload = await response.json();
      const error = (payload as { error?: { message?: string } })?.error;
      if (error?.message) message = error.message;
    } catch {
      // Non-JSON error body, keep the generic message.
    }
    throw new ApiError(message, response.status, payload);
  }

  return (await response.json()) as T;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const url = apiUrl(path);
  let response: Response;
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError(
      `Cannot reach the FlameLens backend at ${API_BASE_URL}. Check that the API is running and that CORS_ORIGINS allows this site.`
    );
  }

  if (!response.ok) {
    let message = `Request failed with HTTP ${response.status}`;
    try {
      const payload = (await response.json()) as { error?: { message?: string } };
      if (payload?.error?.message) message = payload.error.message;
    } catch {
      // keep generic
    }
    throw new ApiError(message, response.status);
  }

  return (await response.json()) as T;
}

/** Absolute URL for a CSV/JSON export download. */
export function exportUrl(
  format: 'csv' | 'json',
  params?: Record<string, QueryValue>,
  investigationId?: string
): string {
  if (!isApiConfigured) return '#';
  const path = investigationId
    ? `/investigations/${encodeURIComponent(investigationId)}/files/export`
    : '/files/export';
  return `${API_BASE_URL}${API_PREFIX}${path}${buildQuery({ ...params, format })}`;
}

export interface InvestigationQuery {
  q?: string;
  research_area?: string;
  sub_research_area?: string;
  flight_platform?: string;
  audit_level?: string;
  has_file_inventory?: boolean;
  sort_by?: 'id' | 'title' | 'start_date' | 'end_date' | 'file_count' | 'remote_size';
  order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export function getInvestigations(query: InvestigationQuery = {}) {
  return request<InvestigationListResponse>('/investigations', { ...query });
}

export function getInvestigation(id: string) {
  return request<InvestigationDetail>(`/investigations/${encodeURIComponent(id)}`);
}

export interface FileQuery {
  q?: string;
  investigation_id?: string;
  extension?: string;
  format_category?: string;
  download_status?: string;
  dataset_id?: string;
  min_size?: number;
  max_size?: number;
  sort_by?: 'filename' | 'size' | 'extension' | 'dataset' | 'investigation';
  order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export function getFiles(query: FileQuery = {}) {
  return request<FileListResponse>('/files', { ...query });
}

export function getInvestigationFiles(id: string, query: FileQuery = {}) {
  return request<FileListResponse>(`/investigations/${encodeURIComponent(id)}/files`, {
    ...query,
  });
}

export function getStorageSummary(id: string) {
  return request<StorageSummaryResponse>(
    `/investigations/${encodeURIComponent(id)}/storage-summary`
  );
}

export function getInvestigationDatasets(id: string) {
  return request<DatasetListResponse>(`/investigations/${encodeURIComponent(id)}/datasets`);
}

export function getOverview() {
  return request<OverviewResponse>('/analytics/overview');
}

export function getStorageAnalytics() {
  return request<StorageAnalyticsResponse>('/analytics/storage');
}

export function getComparison(a: string, b: string) {
  return request<ComparisonResponse>('/comparison', { ids: `${a},${b}` });
}

export function askAssistant(query: string, limit = 4) {
  return post<AssistantResponse>('/assistant/query', { query, limit });
}

/**
 * Checks connectivity and system telemetry from the backend health endpoint.
 * Real HTTP request against GET /api/v1/health.
 */
export async function checkBackendHealth(
  timeoutMs: number = 5000
): Promise<BackendHealthResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(apiUrl('/health'), {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new ApiError(
        `Backend returned HTTP ${response.status}: ${response.statusText}`,
        response.status
      );
    }

    return (await response.json()) as BackendHealthResponse;
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof ApiError) throw err;
    if (err instanceof Error) {
      if (err.name === 'AbortError') {
        throw new ApiError('Backend health request timed out after 5 seconds.');
      }
      throw new ApiError(`Network error connecting to backend: ${err.message}`);
    }
    throw new ApiError('Unknown error connecting to backend.');
  }
}

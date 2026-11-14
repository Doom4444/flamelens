import { BackendHealthResponse } from '../types';

export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000';

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
    const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new ApiError(
        `Backend returned HTTP ${response.status}: ${response.statusText}`,
        response.status
      );
    }

    const data: BackendHealthResponse = await response.json();
    return data;
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof ApiError) {
      throw err;
    }
    if (err instanceof Error) {
      if (err.name === 'AbortError') {
        throw new ApiError('Backend health request timed out after 5 seconds.');
      }
      throw new ApiError(`Network error connecting to backend: ${err.message}`);
    }
    throw new ApiError('Unknown error connecting to backend.');
  }
}

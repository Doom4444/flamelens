import { useState, useEffect, useCallback } from 'react';
import { checkBackendHealth, ApiError } from '../services/api';
import { BackendHealthResponse, ConnectionStatus } from '../types';

export interface UseHealthReturn {
  status: ConnectionStatus;
  data: BackendHealthResponse | null;
  error: string | null;
  lastChecked: Date | null;
  checkNow: () => Promise<void>;
}

export function useHealth(autoRefreshIntervalMs: number = 30000): UseHealthReturn {
  const [status, setStatus] = useState<ConnectionStatus>('checking');
  const [data, setData] = useState<BackendHealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkNow = useCallback(async () => {
    setStatus('checking');
    setError(null);
    try {
      const response = await checkBackendHealth();
      setData(response);
      setStatus('connected');
      setError(null);
    } catch (err: unknown) {
      setStatus('disconnected');
      setData(null);
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Connection failed');
      }
    } finally {
      setLastChecked(new Date());
    }
  }, []);

  useEffect(() => {
    // Initial health check
    checkNow();

    if (autoRefreshIntervalMs <= 0) return;

    const intervalId = setInterval(() => {
      checkNow();
    }, autoRefreshIntervalMs);

    return () => clearInterval(intervalId);
  }, [checkNow, autoRefreshIntervalMs]);

  return {
    status,
    data,
    error,
    lastChecked,
    checkNow,
  };
}

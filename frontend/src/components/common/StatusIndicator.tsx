import React from 'react';
import { ConnectionStatus } from '../../types';
import { RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

interface StatusIndicatorProps {
  status: ConnectionStatus;
  version?: string;
  error?: string | null;
  onRetry?: () => void;
  compact?: boolean;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  version,
  error,
  onRetry,
  compact = false,
}) => {
  if (compact) {
    return (
      <div className="flex items-center space-x-2" title={status === 'connected' ? `Connected to Backend v${version || '0.1.0'}` : error || 'Disconnected'}>
        <span className="relative flex h-2.5 w-2.5">
          {status === 'connected' && (
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          )}
          <span
            className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
              status === 'connected'
                ? 'bg-emerald-500'
                : status === 'checking'
                ? 'bg-amber-400 animate-pulse'
                : 'bg-rose-500'
            }`}
          ></span>
        </span>
        <span className="text-xs font-mono text-[#94A3B8]">
          {status === 'connected' ? 'API LIVE' : status === 'checking' ? 'SYNCING' : 'OFFLINE'}
        </span>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center space-x-3 px-3 py-1.5 rounded-full bg-[#111E30] border border-[#243449] text-xs">
      <span className="relative flex h-2.5 w-2.5">
        {status === 'connected' && (
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
        )}
        <span
          className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
            status === 'connected'
              ? 'bg-emerald-500'
              : status === 'checking'
              ? 'bg-amber-400 animate-pulse'
              : 'bg-rose-500'
          }`}
        ></span>
      </span>

      <span className="font-medium text-[#F4F7FB]">
        {status === 'connected' ? (
          <span className="flex items-center gap-1.5 text-emerald-400">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Backend Connected {version && <span className="text-[#94A3B8] font-mono text-[11px]">(v{version})</span>}
          </span>
        ) : status === 'checking' ? (
          <span className="flex items-center gap-1.5 text-amber-400">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            Checking Backend Connection...
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-rose-400">
            <AlertCircle className="w-3.5 h-3.5" />
            Backend Disconnected
          </span>
        )}
      </span>

      {status === 'disconnected' && onRetry && (
        <button
          onClick={onRetry}
          className="ml-1 px-2 py-0.5 rounded bg-[#243449] hover:bg-[#334760] text-[#35C6E8] text-[11px] font-mono transition-colors"
          title={error || 'Click to retry connection'}
        >
          Retry
        </button>
      )}
    </div>
  );
};

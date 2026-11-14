import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Unable to load data',
  message,
  onRetry,
}) => (
  <div className="flex flex-col items-center justify-center rounded-lg border border-rose-400/25 bg-rose-400/5 p-10 text-center">
    <div className="mb-4 rounded-full border border-rose-400/25 bg-rose-400/10 p-3">
      <AlertTriangle className="h-6 w-6 text-rose-300" />
    </div>
    <h3 className="mb-1 text-base font-semibold text-[#F4F7FB]">{title}</h3>
    <p className="mb-5 max-w-xl text-sm text-[#94A3B8]">{message}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 rounded-md border border-[#243449] bg-[#111E30] px-4 py-2 text-sm font-medium text-[#F4F7FB] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8]"
      >
        <RefreshCw className="h-4 w-4" />
        Retry
      </button>
    )}
  </div>
);

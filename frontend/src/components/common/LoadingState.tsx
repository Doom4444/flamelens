import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading scientific telemetry...',
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <Loader2 className="w-8 h-8 text-[#35C6E8] animate-spin mb-3" />
      <p className="text-sm font-mono text-[#94A3B8]">{message}</p>
    </div>
  );
};

import React from 'react';
import { Menu, ExternalLink, Globe } from 'lucide-react';
import { StatusIndicator } from '../common/StatusIndicator';
import { ConnectionStatus } from '../../types';

interface HeaderProps {
  onOpenSidebar: () => void;
  connectionStatus: ConnectionStatus;
  backendVersion?: string;
  connectionError?: string | null;
  onRetryConnection: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenSidebar,
  connectionStatus,
  backendVersion,
  connectionError,
  onRetryConnection,
}) => {
  return (
    <header className="sticky top-0 z-30 h-16 bg-[#080F1C]/80 backdrop-blur-md border-b border-[#243449] px-4 sm:px-6 lg:px-8 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenSidebar}
          className="p-2 rounded-md text-[#94A3B8] hover:text-[#F4F7FB] hover:bg-[#111E30] lg:hidden"
          aria-label="Open sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-[#94A3B8]">
          <span className="text-[#35C6E8]">MISSION</span>
          <span>/</span>
          <span>MICROGRAVITY COMBUSTION INTELLIGENCE</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Live Status Indicator */}
        <StatusIndicator
          status={connectionStatus}
          version={backendVersion}
          error={connectionError}
          onRetry={onRetryConnection}
          compact={false}
        />

        {/* NASA PSI Link */}
        <a
          href="https://psi.nasa.gov/physci/repo/search?q=combustion"
          target="_blank"
          rel="noopener noreferrer"
          className="hidden md:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#111E30] border border-[#243449] hover:border-[#35C6E8] text-xs font-medium text-[#F4F7FB] hover:text-[#35C6E8] transition-all"
        >
          <Globe className="w-3.5 h-3.5 text-[#35C6E8]" />
          <span>NASA PSI Repository</span>
          <ExternalLink className="w-3 h-3 text-[#94A3B8]" />
        </a>
      </div>
    </header>
  );
};

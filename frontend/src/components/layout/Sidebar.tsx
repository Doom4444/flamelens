import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  FolderSearch,
  HardDrive,
  Scale,
  Sparkles,
  Flame,
  X,
  ExternalLink,
} from 'lucide-react';
import { StatusIndicator } from '../common/StatusIndicator';
import { ConnectionStatus } from '../../types';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  connectionStatus: ConnectionStatus;
  backendVersion?: string;
}

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
  badge?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  connectionStatus,
  backendVersion,
}) => {
  const navItems: NavItem[] = [
    { name: 'Overview', path: '/overview', icon: LayoutDashboard },
    { name: 'Investigations', path: '/investigations', icon: Search },
    { name: 'File Explorer', path: '/files', icon: FolderSearch },
    { name: 'Storage Analytics', path: '/storage', icon: HardDrive },
    { name: 'Comparison Studio', path: '/comparison', icon: Scale },
    { name: 'AI Assistant', path: '/assistant', icon: Sparkles, badge: 'RAG' },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-[#0C1626] border-r border-[#243449] flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-[#243449]">
          <NavLink to="/overview" className="flex items-center gap-3 group">
            <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-[#111E30] border border-[#243449] group-hover:border-[#35C6E8] transition-colors">
              <Flame className="w-5 h-5 text-[#FF914D]" />
              <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-[#35C6E8]"></span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-base font-bold tracking-tight text-[#F4F7FB] font-sans">
                  Flame<span className="text-[#35C6E8]">Lens</span>
                </span>
              </div>
              <p className="text-[10px] font-mono tracking-wider uppercase text-[#94A3B8]">
                NASA Space Apps 2026
              </p>
            </div>
          </NavLink>

          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-[#94A3B8] hover:text-[#F4F7FB] hover:bg-[#111E30] lg:hidden"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Challenge Identification Banner */}
        <div className="px-4 py-3 mx-3 my-3 rounded-md bg-[#111E30]/70 border border-[#243449]/70">
          <div className="flex items-center justify-between text-[11px] font-mono text-[#94A3B8] mb-1">
            <span>CHALLENGE</span>
            <span className="text-[#FF914D] font-semibold">FREEFALL</span>
          </div>
          <p className="text-xs text-[#F4F7FB] font-medium leading-snug">
            Flame in Freefall: Microgravity Combustion
          </p>
        </div>

        {/* Primary Navigation */}
        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-md text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-[#111E30] text-[#35C6E8] border-l-2 border-[#35C6E8] shadow-sm font-semibold'
                      : 'text-[#94A3B8] hover:text-[#F4F7FB] hover:bg-[#111E30]/60'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-[#35C6E8]/10 text-[#35C6E8] border border-[#35C6E8]/20">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Footer / System Status */}
        <div className="p-4 border-t border-[#243449] bg-[#080F1C]/40 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase text-[#64748B]">Telemetry</span>
            <StatusIndicator
              status={connectionStatus}
              version={backendVersion}
              compact={true}
            />
          </div>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between text-xs font-mono text-[#94A3B8] hover:text-[#35C6E8] transition-colors pt-2 border-t border-[#243449]/40"
          >
            <span>FastAPI Docs</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </aside>
    </>
  );
};

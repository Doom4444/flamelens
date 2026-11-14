import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useHealth } from '../../hooks/useHealth';

export const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { status, data, error, checkNow } = useHealth();

  return (
    <div className="min-h-screen bg-[#080F1C] text-[#F4F7FB] flex">
      {/* Sidebar Navigation */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        connectionStatus={status}
        backendVersion={data?.version}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-64">
        <Header
          onOpenSidebar={() => setSidebarOpen(true)}
          connectionStatus={status}
          backendVersion={data?.version}
          connectionError={error}
          onRetryConnection={checkNow}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>

        <footer className="py-6 px-4 sm:px-6 lg:px-8 border-t border-[#243449] bg-[#0C1626]/40 text-xs text-[#94A3B8] font-mono">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <span>FlameLens — NASA Space Apps Challenge 2026</span>
              <span className="mx-2 text-[#243449]">|</span>
              <span>Primary Source: NASA Physical Sciences Informatics (PSI)</span>
            </div>
            <div className="text-[11px] text-[#64748B]">
              Autonomous Microgravity Combustion Intelligence Architecture
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

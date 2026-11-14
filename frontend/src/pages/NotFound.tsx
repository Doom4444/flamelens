import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertOctagon, ArrowLeft } from 'lucide-react';

export const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center p-6">
      <div className="p-4 rounded-full bg-[#111E30] border border-[#243449] mb-4 text-[#FF914D]">
        <AlertOctagon className="w-10 h-10" />
      </div>

      <span className="text-xs font-mono text-[#35C6E8] uppercase tracking-wider mb-1">
        Error 404
      </span>

      <h1 className="text-2xl sm:text-3xl font-bold text-[#F4F7FB] mb-2">
        Trajectory Lost / Page Not Found
      </h1>

      <p className="text-sm text-[#94A3B8] max-w-md mb-6 leading-relaxed">
        The requested scientific pathway or resource does not exist in the FlameLens mission map.
      </p>

      <button
        onClick={() => navigate('/overview')}
        className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[#35C6E8] text-[#080F1C] font-semibold text-sm hover:bg-[#35C6E8]/90 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Return to Mission Overview</span>
      </button>
    </div>
  );
};

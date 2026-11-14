import React from 'react';
import { LucideIcon, Clock } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  description: string;
  icon: LucideIcon;
  isPending?: boolean;
  statusLabel?: string;
  accentColor?: 'cyan' | 'orange' | 'blue' | 'purple';
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  description,
  icon: Icon,
  isPending = false,
  statusLabel = 'Data ingestion pending',
  accentColor = 'cyan',
}) => {
  const accentClasses = {
    cyan: 'border-l-[#35C6E8] text-[#35C6E8]',
    orange: 'border-l-[#FF914D] text-[#FF914D]',
    blue: 'border-l-blue-400 text-blue-400',
    purple: 'border-l-indigo-400 text-indigo-400',
  }[accentColor];

  const iconBgClasses = {
    cyan: 'bg-[#35C6E8]/10 text-[#35C6E8]',
    orange: 'bg-[#FF914D]/10 text-[#FF914D]',
    blue: 'bg-blue-400/10 text-blue-400',
    purple: 'bg-indigo-400/10 text-indigo-400',
  }[accentColor];

  return (
    <div
      className={`relative p-5 rounded-lg bg-[#111E30] border border-[#243449] border-l-4 ${accentClasses} shadow-sm hover:border-[#334760] transition-all`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase font-mono tracking-wider text-[#94A3B8]">
            {label}
          </p>
          <div className="mt-2 flex items-baseline gap-2">
            {isPending ? (
              <span className="text-xl font-mono font-semibold text-[#94A3B8] flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-[#94A3B8] inline" />
                Pending
              </span>
            ) : (
              <span className="text-2xl font-mono font-bold text-[#F4F7FB]">
                {value}
              </span>
            )}
          </div>
        </div>
        <div className={`p-2.5 rounded-md ${iconBgClasses}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-[#243449]/60 flex items-center justify-between text-xs">
        <span className="text-[#94A3B8]">{description}</span>
        {isPending && (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#080F1C] border border-[#243449] text-amber-400">
            {statusLabel}
          </span>
        )}
      </div>
    </div>
  );
};

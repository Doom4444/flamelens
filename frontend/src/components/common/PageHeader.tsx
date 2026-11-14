import React from 'react';

interface PageHeaderProps {
  title: string;
  subtitle: string;
  badge?: string;
  action?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  badge,
  action,
}) => {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 mb-8 border-b border-[#243449] gap-4">
      <div>
        <div className="flex items-center gap-2.5 mb-1.5">
          <h1 className="text-2xl font-bold tracking-tight text-[#F4F7FB]">
            {title}
          </h1>
          {badge && (
            <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-[#35C6E8]/10 text-[#35C6E8] border border-[#35C6E8]/30">
              {badge}
            </span>
          )}
        </div>
        <p className="text-sm text-[#94A3B8] max-w-3xl leading-relaxed">
          {subtitle}
        </p>
      </div>

      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  );
};

import React, { ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';

interface PanelProps {
  title: string;
  subtitle?: string;
  icon?: LucideIcon;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export const Panel: React.FC<PanelProps> = ({
  title,
  subtitle,
  icon: Icon,
  action,
  children,
  className = '',
}) => (
  <section className={`rounded-lg border border-[#243449] bg-[#111E30] p-5 ${className}`}>
    <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
      <div className="flex items-start gap-2.5">
        {Icon && (
          <div className="mt-0.5 rounded-md border border-[#243449] bg-[#0C1626] p-1.5 text-[#35C6E8]">
            <Icon className="h-4 w-4" />
          </div>
        )}
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[#F4F7FB]">
            {title}
          </h2>
          {subtitle && <p className="mt-0.5 text-xs text-[#94A3B8]">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
    {children}
  </section>
);

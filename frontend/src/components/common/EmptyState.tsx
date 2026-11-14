import React from 'react';
import { LucideIcon, Database } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: LucideIcon;
  actionText?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon = Database,
  actionText,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-lg bg-[#111E30]/50 border border-dashed border-[#243449]">
      <div className="p-4 rounded-full bg-[#0C1626] border border-[#243449] mb-4 text-[#94A3B8]">
        <Icon className="w-8 h-8 text-[#35C6E8]" />
      </div>
      <h3 className="text-base font-semibold text-[#F4F7FB] mb-1">{title}</h3>
      <p className="text-sm text-[#94A3B8] max-w-md mb-6">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 rounded-md bg-[#243449] hover:bg-[#334760] text-sm font-medium text-[#F4F7FB] transition-colors"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};

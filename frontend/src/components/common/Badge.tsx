import React from 'react';

export type BadgeTone =
  | 'cyan'
  | 'orange'
  | 'green'
  | 'amber'
  | 'red'
  | 'slate'
  | 'purple';

const TONES: Record<BadgeTone, string> = {
  cyan: 'bg-[#35C6E8]/10 text-[#35C6E8] border-[#35C6E8]/25',
  orange: 'bg-[#FF914D]/10 text-[#FF914D] border-[#FF914D]/25',
  green: 'bg-emerald-400/10 text-emerald-300 border-emerald-400/25',
  amber: 'bg-amber-400/10 text-amber-300 border-amber-400/25',
  red: 'bg-rose-400/10 text-rose-300 border-rose-400/25',
  slate: 'bg-[#0C1626] text-[#94A3B8] border-[#243449]',
  purple: 'bg-indigo-400/10 text-indigo-300 border-indigo-400/25',
};

interface BadgeProps {
  children: React.ReactNode;
  tone?: BadgeTone;
  className?: string;
  title?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  tone = 'slate',
  className = '',
  title,
}) => (
  <span
    title={title}
    className={`inline-flex items-center gap-1 rounded border px-2 py-0.5 text-[11px] font-mono font-medium leading-4 whitespace-nowrap ${TONES[tone]} ${className}`}
  >
    {children}
  </span>
);

export function downloadStatusTone(status: string): BadgeTone {
  switch (status) {
    case 'DOWNLOADED':
      return 'green';
    case 'PENDING':
      return 'amber';
    case 'OVER_LIMIT':
      return 'red';
    case 'HISTORICAL_REMOVED':
      return 'slate';
    case 'FAILED':
      return 'red';
    default:
      return 'slate';
  }
}

export function downloadStatusLabel(status: string): string {
  switch (status) {
    case 'PENDING':
      return 'Eligible · not downloaded';
    case 'OVER_LIMIT':
      return 'Over 100 MiB limit';
    case 'HISTORICAL_REMOVED':
      return 'Historical · removed';
    case 'DOWNLOADED':
      return 'Downloaded locally';
    case 'FAILED':
      return 'Download failed';
    default:
      return status;
  }
}

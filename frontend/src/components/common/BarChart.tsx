import React from 'react';
import { formatNumber } from '../../utils/format';

export interface BarChartItem {
  label: string;
  value: number;
  valueLabel?: string;
  hint?: string;
  tone?: 'cyan' | 'orange' | 'purple' | 'green' | 'slate';
}

interface BarChartProps {
  data: BarChartItem[];
  onSelect?: (item: BarChartItem) => void;
  emptyMessage?: string;
}

const TONE_CLASSES: Record<string, string> = {
  cyan: 'bg-[#35C6E8]',
  orange: 'bg-[#FF914D]',
  purple: 'bg-indigo-400',
  green: 'bg-emerald-400',
  slate: 'bg-[#64748B]',
};

export const BarChart: React.FC<BarChartProps> = ({
  data,
  onSelect,
  emptyMessage = 'No data available.',
}) => {
  if (data.length === 0) {
    return <p className="py-6 text-center text-sm text-[#64748B]">{emptyMessage}</p>;
  }
  const max = Math.max(...data.map((item) => item.value), 1);

  return (
    <div className="space-y-2.5">
      {data.map((item) => {
        const width = Math.max(2, (item.value / max) * 100);
        const content = (
          <>
            <div className="mb-1 flex items-center justify-between gap-3 text-xs">
              <span
                className={`truncate font-mono ${
                  onSelect ? 'text-[#94A3B8] group-hover:text-[#35C6E8]' : 'text-[#94A3B8]'
                }`}
                title={item.label}
              >
                {item.label}
              </span>
              <span className="flex-shrink-0 font-mono text-[#F4F7FB]">
                {item.valueLabel ?? formatNumber(item.value)}
              </span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#0C1626]">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  TONE_CLASSES[item.tone ?? 'cyan']
                }`}
                style={{ width: `${width}%` }}
              />
            </div>
            {item.hint && <p className="mt-1 text-[10px] text-[#64748B]">{item.hint}</p>}
          </>
        );

        if (onSelect) {
          return (
            <button
              key={item.label}
              type="button"
              onClick={() => onSelect(item)}
              className="group block w-full rounded-md p-1 text-left transition-colors hover:bg-[#0C1626]/60"
              title={`Filter by ${item.label}`}
            >
              {content}
            </button>
          );
        }

        return (
          <div key={item.label} className="rounded-md p-1">
            {content}
          </div>
        );
      })}
    </div>
  );
};

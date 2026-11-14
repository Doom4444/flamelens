import React from 'react';
import { formatNumber } from '../../utils/format';

export interface DonutSlice {
  label: string;
  value: number;
}

interface DonutChartProps {
  data: DonutSlice[];
  centerLabel?: string;
  centerValue?: string;
  size?: number;
}

export const DONUT_COLORS = [
  '#35C6E8',
  '#FF914D',
  '#818CF8',
  '#34D399',
  '#F472B6',
  '#FBBF24',
  '#94A3B8',
  '#22D3EE',
];

export const DonutChart: React.FC<DonutChartProps> = ({
  data,
  centerLabel,
  centerValue,
  size = 168,
}) => {
  const total = data.reduce((sum, slice) => sum + slice.value, 0);
  if (total <= 0) {
    return <p className="py-6 text-center text-sm text-[#64748B]">No data available.</p>;
  }

  const radius = 44;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  return (
    <div className="flex flex-col items-center gap-5 sm:flex-row sm:items-center">
      <svg
        width={size}
        height={size}
        viewBox="0 0 120 120"
        role="img"
        aria-label="Distribution chart"
        className="flex-shrink-0"
      >
        <circle cx="60" cy="60" r={radius} fill="none" stroke="#0C1626" strokeWidth="14" />
        {data.map((slice, index) => {
          const fraction = slice.value / total;
          const dash = fraction * circumference;
          const dashOffset = -offset;
          offset += dash;
          return (
            <circle
              key={slice.label}
              cx="60"
              cy="60"
              r={radius}
              fill="none"
              stroke={DONUT_COLORS[index % DONUT_COLORS.length]}
              strokeWidth="14"
              strokeDasharray={`${dash} ${circumference - dash}`}
              strokeDashoffset={dashOffset}
              transform="rotate(-90 60 60)"
              className="transition-opacity hover:opacity-75"
            >
              <title>
                {slice.label}: {formatNumber(slice.value)} (
                {((fraction * 100) as number).toFixed(1)}%)
              </title>
            </circle>
          );
        })}
        <text
          x="60"
          y="56"
          textAnchor="middle"
          className="fill-[#F4F7FB] font-mono"
          fontSize="14"
          fontWeight="700"
        >
          {centerValue ?? formatNumber(total)}
        </text>
        <text
          x="60"
          y="70"
          textAnchor="middle"
          className="fill-[#94A3B8] font-mono"
          fontSize="7"
        >
          {centerLabel ?? 'TOTAL'}
        </text>
      </svg>

      <ul className="w-full space-y-1.5">
        {data.map((slice, index) => (
          <li key={slice.label} className="flex items-center justify-between gap-3 text-xs">
            <span className="flex min-w-0 items-center gap-2">
              <span
                className="h-2.5 w-2.5 flex-shrink-0 rounded-sm"
                style={{ backgroundColor: DONUT_COLORS[index % DONUT_COLORS.length] }}
              />
              <span className="truncate text-[#94A3B8]">{slice.label}</span>
            </span>
            <span className="flex-shrink-0 font-mono text-[#F4F7FB]">
              {formatNumber(slice.value)}
              <span className="ml-1 text-[#64748B]">
                {total ? `${((slice.value / total) * 100).toFixed(1)}%` : '0%'}
              </span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

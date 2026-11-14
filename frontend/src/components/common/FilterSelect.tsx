import React from 'react';
import { ChevronDown } from 'lucide-react';

export interface FilterOption {
  value: string;
  label: string;
}

interface FilterSelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: FilterOption[];
  allowAll?: boolean;
  allLabel?: string;
}

export const FilterSelect: React.FC<FilterSelectProps> = ({
  label,
  value,
  onChange,
  options,
  allowAll = true,
  allLabel = 'All',
}) => (
  <label className="block min-w-0">
    <span className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
      {label}
    </span>
    <div className="relative">
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full appearance-none rounded-md border border-[#243449] bg-[#0C1626] py-2 pl-3 pr-8 text-xs text-[#F4F7FB] outline-none transition-colors focus:border-[#35C6E8]"
      >
        {allowAll && <option value="">{allLabel}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#64748B]" />
    </div>
  </label>
);

import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { PaginationMeta } from '../../types';

interface PaginationProps {
  pagination: PaginationMeta;
  onPageChange: (page: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({ pagination, onPageChange }) => {
  const { page, total_pages, total_items, page_size } = pagination;
  if (total_pages <= 1) {
    return (
      <p className="text-xs font-mono text-[#64748B]">
        {total_items} {total_items === 1 ? 'record' : 'records'}
      </p>
    );
  }

  const windowStart = Math.max(1, Math.min(page - 2, total_pages - 4));
  const windowEnd = Math.min(total_pages, windowStart + 4);
  const pages: number[] = [];
  for (let index = windowStart; index <= windowEnd; index += 1) pages.push(index);

  const firstItem = (page - 1) * page_size + 1;
  const lastItem = Math.min(page * page_size, total_items);

  return (
    <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
      <p className="text-xs font-mono text-[#64748B]">
        Showing {firstItem}–{lastItem} of {total_items} records
      </p>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={!pagination.has_previous}
          className="rounded-md border border-[#243449] bg-[#111E30] p-2 text-[#94A3B8] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8] disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="Previous page"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        {windowStart > 1 && (
          <>
            <button
              onClick={() => onPageChange(1)}
              className="hidden rounded-md border border-[#243449] bg-[#111E30] px-3 py-1.5 text-xs font-mono text-[#94A3B8] hover:text-[#35C6E8] sm:block"
            >
              1
            </button>
            <span className="px-1 text-xs text-[#64748B]">…</span>
          </>
        )}
        {pages.map((value) => (
          <button
            key={value}
            onClick={() => onPageChange(value)}
            className={`rounded-md border px-3 py-1.5 text-xs font-mono transition-colors ${
              value === page
                ? 'border-[#35C6E8]/50 bg-[#35C6E8]/10 text-[#35C6E8]'
                : 'border-[#243449] bg-[#111E30] text-[#94A3B8] hover:border-[#35C6E8] hover:text-[#35C6E8]'
            }`}
          >
            {value}
          </button>
        ))}
        {windowEnd < total_pages && (
          <>
            <span className="px-1 text-xs text-[#64748B]">…</span>
            <button
              onClick={() => onPageChange(total_pages)}
              className="hidden rounded-md border border-[#243449] bg-[#111E30] px-3 py-1.5 text-xs font-mono text-[#94A3B8] hover:text-[#35C6E8] sm:block"
            >
              {total_pages}
            </button>
          </>
        )}
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={!pagination.has_next}
          className="rounded-md border border-[#243449] bg-[#111E30] p-2 text-[#94A3B8] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8] disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="Next page"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

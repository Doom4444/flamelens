import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Download, FileWarning, FolderSearch, Search, X } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { FileTable, FileSortField } from '../components/common/FileTable';
import { FilterSelect } from '../components/common/FilterSelect';
import { Pagination } from '../components/common/Pagination';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { Badge, downloadStatusLabel, downloadStatusTone } from '../components/common/Badge';
import { useApi, useDebouncedValue } from '../hooks/useApi';
import { exportUrl, getFiles, getInvestigations, getOverview } from '../services/api';
import { formatNumber } from '../utils/format';
const STATUS_OPTIONS = ['PENDING', 'OVER_LIMIT', 'HISTORICAL_REMOVED', 'DOWNLOADED', 'FAILED'];

export const Files: React.FC = () => {
  const [searchParams] = useSearchParams();

  const [query, setQuery] = useState('');
  const [investigation, setInvestigation] = useState(
    searchParams.get('investigation') ?? ''
  );
  const [extension, setExtension] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [sortBy, setSortBy] = useState<FileSortField>('filename');
  const [order, setOrder] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(1);
  const debouncedQuery = useDebouncedValue(query);

  const overview = useApi(getOverview, []);
  const investigations = useApi(
    () => getInvestigations({ has_file_inventory: true, page_size: 100 }),
    []
  );

  const files = useApi(
    () =>
      getFiles({
        q: debouncedQuery || undefined,
        investigation_id: investigation || undefined,
        extension: extension || undefined,
        format_category: category || undefined,
        download_status: status || undefined,
        sort_by: sortBy,
        order,
        page,
        page_size: 25,
      }),
    [debouncedQuery, investigation, extension, category, status, sortBy, order, page]
  );

  const resetFilters = () => {
    setQuery('');
    setInvestigation('');
    setExtension('');
    setCategory('');
    setStatus('');
    setSortBy('filename');
    setOrder('asc');
    setPage(1);
  };

  const toggleSort = (field: FileSortField) => {
    if (sortBy === field) {
      setOrder((value) => (value === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(field);
      setOrder('asc');
    }
    setPage(1);
  };

  const filters = {
    q: debouncedQuery || undefined,
    investigation_id: investigation || undefined,
    extension: extension || undefined,
    format_category: category || undefined,
    download_status: status || undefined,
    sort_by: sortBy,
    order,
  };

  const hasActiveFilters =
    Boolean(query) || Boolean(investigation) || Boolean(extension) || Boolean(category) || Boolean(status);

  return (
    <div className="space-y-6">
      <PageHeader
        title="File Explorer"
        subtitle="Search the 1,520 audited NASA PSI file records. Remote inventory sizes are shown separately from local storage, which is 0 B."
        badge="1,520 files"
        action={
          <div className="flex flex-wrap gap-2">
            <a
              href={exportUrl('csv', filters, investigation || undefined)}
              className="inline-flex items-center gap-2 rounded-md border border-[#35C6E8]/40 bg-[#35C6E8]/10 px-3 py-2 text-xs font-medium text-[#35C6E8] transition-colors hover:bg-[#35C6E8]/20"
            >
              <Download className="h-3.5 w-3.5" /> Export CSV
            </a>
            <a
              href={exportUrl('json', filters, investigation || undefined)}
              className="inline-flex items-center gap-2 rounded-md border border-[#243449] bg-[#111E30] px-3 py-2 text-xs font-medium text-[#F4F7FB] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8]"
            >
              <Download className="h-3.5 w-3.5" /> Export JSON
            </a>
          </div>
        }
      />

      <section className="rounded-lg border border-[#243449] bg-[#111E30] p-4">
        <div className="mb-3 flex items-center justify-between gap-2">
          <span className="font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
            Search and filters
          </span>
          {hasActiveFilters && (
            <button
              onClick={resetFilters}
              className="inline-flex items-center gap-1 text-[11px] font-medium text-[#94A3B8] transition-colors hover:text-[#FF914D]"
            >
              <X className="h-3 w-3" /> Clear filters
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-6">
          <label className="block md:col-span-2">
            <span className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
              Filename search
            </span>
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#64748B]" />
              <input
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setPage(1);
                }}
                placeholder="raw data, iss040, pdf..."
                className="w-full rounded-md border border-[#243449] bg-[#0C1626] py-2 pl-9 pr-3 text-xs text-[#F4F7FB] outline-none transition-colors placeholder:text-[#64748B] focus:border-[#35C6E8]"
              />
            </div>
          </label>

          <FilterSelect
            label="Investigation"
            value={investigation}
            onChange={(value) => {
              setInvestigation(value);
              setPage(1);
            }}
            options={(investigations.data?.items ?? []).map((item) => ({
              value: item.investigation_id,
              label: `${item.investigation_id} · ${item.acronym ?? item.title.slice(0, 32)}`,
            }))}
            allLabel="All investigations"
          />

          <FilterSelect
            label="Format category"
            value={category}
            onChange={(value) => {
              setCategory(value);
              setPage(1);
            }}
            options={(overview.data?.format_category_distribution ?? []).map((row) => ({
              value: row.format_category,
              label: `${row.format_category} (${row.count})`,
            }))}
            allLabel="All categories"
          />

          <FilterSelect
            label="Extension"
            value={extension}
            onChange={(value) => {
              setExtension(value);
              setPage(1);
            }}
            options={(overview.data?.file_type_distribution ?? []).map((row) => ({
              value: row.extension,
              label: `${row.extension} (${row.count})`,
            }))}
            allLabel="All extensions"
          />

          <FilterSelect
            label="Download status"
            value={status}
            onChange={(value) => {
              setStatus(value);
              setPage(1);
            }}
            options={STATUS_OPTIONS.map((value) => ({
              value,
              label: downloadStatusLabel(value),
            }))}
            allLabel="All statuses"
          />
        </div>
      </section>

      {files.loading && <LoadingState message="Loading file inventory..." />}
      {!files.loading && files.error && <ErrorState message={files.error} onRetry={files.reload} />}

      {!files.loading && !files.error && files.data && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div className="rounded-lg border border-[#243449] bg-[#111E30] p-3.5">
              <p className="font-mono text-[9px] uppercase tracking-wider text-[#64748B]">
                Matching files
              </p>
              <p className="mt-1 font-mono text-lg font-bold text-[#F4F7FB]">
                {formatNumber(files.data.totals.total_items)}
              </p>
            </div>
            <div className="rounded-lg border border-[#243449] bg-[#111E30] p-3.5">
              <p className="font-mono text-[9px] uppercase tracking-wider text-[#64748B]">
                Remote size (filtered)
              </p>
              <p className="mt-1 font-mono text-lg font-bold text-[#35C6E8]">
                {files.data.totals.remote_size_human}
              </p>
            </div>
            <div className="rounded-lg border border-[#243449] bg-[#111E30] p-3.5">
              <p className="font-mono text-[9px] uppercase tracking-wider text-[#64748B]">
                Known / unknown size
              </p>
              <p className="mt-1 font-mono text-lg font-bold text-[#F4F7FB]">
                {formatNumber(files.data.totals.known_size_items)} /{' '}
                {formatNumber(files.data.totals.unknown_size_items)}
              </p>
            </div>
            <div className="rounded-lg border border-[#243449] bg-[#111E30] p-3.5">
              <p className="font-mono text-[9px] uppercase tracking-wider text-[#64748B]">
                Local downloaded
              </p>
              <p className="mt-1 font-mono text-lg font-bold text-[#FF914D]">
                {files.data.totals.local_downloaded_size_human}
              </p>
            </div>
          </div>

          <div className="rounded-lg border border-[#243449] bg-[#111E30] p-5">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(files.data.totals.by_status).map(([key, value]) => (
                  <Badge key={key} tone={downloadStatusTone(key)}>
                    {downloadStatusLabel(key)}: {formatNumber(value)}
                  </Badge>
                ))}
              </div>
              <p className="font-mono text-[10px] text-[#64748B]">
                Page {files.data.pagination.page} of {files.data.pagination.total_pages}
              </p>
            </div>

            {files.data.items.length === 0 ? (
              <EmptyState
                icon={FolderSearch}
                title="No files match"
                description="No audited NASA PSI file records match the current search and filters. Adjust the filters or clear them to browse the full inventory."
                actionText="Clear filters"
                onAction={resetFilters}
              />
            ) : (
              <>
                <FileTable
                  files={files.data.items}
                  showInvestigation
                  sortBy={sortBy}
                  order={order}
                  onSort={toggleSort}
                />
                <div className="mt-4 border-t border-[#243449]/60 pt-4">
                  <Pagination
                    pagination={files.data.pagination}
                    onPageChange={(value) => {
                      setPage(value);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                  />
                </div>
              </>
            )}
          </div>

          <div className="rounded-lg border border-[#243449] bg-[#0C1626]/60 p-4">
            <div className="mb-2 flex items-center gap-2">
              <FileWarning className="h-4 w-4 text-[#FF914D]" />
              <h3 className="text-xs font-semibold uppercase tracking-wide text-[#F4F7FB]">
                How to read file status
              </h3>
            </div>
            <ul className="grid gap-2 text-[11px] leading-relaxed text-[#94A3B8] sm:grid-cols-2">
              <li>
                <span className="font-mono text-amber-300">Eligible · not downloaded</span> —
                file is within the 100 MiB policy limit but no bytes have been downloaded.
              </li>
              <li>
                <span className="font-mono text-rose-300">Over 100 MiB limit</span> — inventoried
                for size accounting but explicitly excluded from automatic download.
              </li>
              <li>
                <span className="font-mono text-[#94A3B8]">Historical · removed</span> — the file
                was removed upstream; its audit record is preserved.
              </li>
              <li>
                <span className="font-mono text-emerald-300">Downloaded locally</span> — only
                shown if FlameLens actually holds the file locally (currently none).
              </li>
            </ul>
            <p className="mt-2 text-[11px] text-[#64748B]">
              “PSI source” opens NASA’s download endpoint. It returns a signed S3 redirect and
              is not a direct file mirror. FlameLens does not claim any file is available
              locally.
            </p>
          </div>
        </>
      )}
    </div>
  );
};

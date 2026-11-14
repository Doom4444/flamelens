import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowDownWideNarrow, Search, SlidersHorizontal, X } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { InvestigationCard } from '../components/common/InvestigationCard';
import { FilterSelect } from '../components/common/FilterSelect';
import { Pagination } from '../components/common/Pagination';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { useApi, useDebouncedValue } from '../hooks/useApi';
import { getInvestigations, InvestigationQuery } from '../services/api';
import { formatNumber } from '../utils/format';

const SORT_OPTIONS = [
  { value: 'id', label: 'Investigation ID' },
  { value: 'title', label: 'Title (A–Z)' },
  { value: 'start_date', label: 'Start date' },
  { value: 'file_count', label: 'File count' },
  { value: 'remote_size', label: 'Remote inventory size' },
];

export const Investigations: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [query, setQuery] = useState(searchParams.get('q') ?? '');
  const [researchArea, setResearchArea] = useState(searchParams.get('research_area') ?? '');
  const [platform, setPlatform] = useState('');
  const [inventory, setInventory] = useState('');
  const [sortBy, setSortBy] = useState<InvestigationQuery['sort_by']>('id');
  const [order, setOrder] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(1);
  const debouncedQuery = useDebouncedValue(query);

  const { data, loading, error, reload } = useApi(
    () =>
      getInvestigations({
        q: debouncedQuery || undefined,
        research_area: researchArea || undefined,
        flight_platform: platform || undefined,
        has_file_inventory: inventory === '' ? undefined : inventory === 'yes',
        sort_by: sortBy,
        order,
        page,
        page_size: 12,
      }),
    [debouncedQuery, researchArea, platform, inventory, sortBy, order, page]
  );

  const resetFilters = () => {
    setQuery('');
    setResearchArea('');
    setPlatform('');
    setInventory('');
    setSortBy('id');
    setOrder('asc');
    setPage(1);
  };

  const hasActiveFilters =
    Boolean(query) || Boolean(researchArea) || Boolean(platform) || Boolean(inventory);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Investigation Explorer"
        subtitle="Search all 26 NASA PSI combustion investigations by ID, title, research area, platform, or audited file availability."
        badge="26 records"
      />

      <section className="rounded-lg border border-[#243449] bg-[#111E30] p-4">
        <div className="mb-3 flex items-center justify-between gap-2">
          <span className="inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
            <SlidersHorizontal className="h-3.5 w-3.5 text-[#35C6E8]" />
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
          <label className="block xl:col-span-2">
            <span className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
              Search
            </span>
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#64748B]" />
              <input
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setPage(1);
                }}
                placeholder="PSI-25, BASS-II, suppression, ISS..."
                className="w-full rounded-md border border-[#243449] bg-[#0C1626] py-2 pl-9 pr-3 text-xs text-[#F4F7FB] outline-none transition-colors placeholder:text-[#64748B] focus:border-[#35C6E8]"
              />
            </div>
          </label>

          <FilterSelect
            label="Research area"
            value={researchArea}
            onChange={(value) => {
              setResearchArea(value);
              setPage(1);
            }}
            options={(data?.facets.research_areas ?? []).map((value) => ({
              value,
              label: value,
            }))}
            allLabel="All research areas"
          />

          <FilterSelect
            label="Flight platform"
            value={platform}
            onChange={(value) => {
              setPlatform(value);
              setPage(1);
            }}
            options={(data?.facets.flight_platforms ?? []).map((value) => ({
              value,
              label: value,
            }))}
            allLabel="All platforms"
          />

          <FilterSelect
            label="File inventory"
            value={inventory}
            onChange={(value) => {
              setInventory(value);
              setPage(1);
            }}
            options={[
              { value: 'yes', label: 'Audited inventory only' },
              { value: 'no', label: 'Metadata only' },
            ]}
            allLabel="Any audit level"
          />

          <div className="flex items-end gap-2">
            <div className="min-w-0 flex-1">
              <FilterSelect
                label="Sort by"
                value={sortBy ?? 'id'}
                onChange={(value) => {
                  setSortBy(value as InvestigationQuery['sort_by']);
                  setPage(1);
                }}
                options={SORT_OPTIONS}
                allowAll={false}
              />
            </div>
            <button
              onClick={() => {
                setOrder((value) => (value === 'asc' ? 'desc' : 'asc'));
                setPage(1);
              }}
              title={`Toggle ${order === 'asc' ? 'descending' : 'ascending'} order`}
              className="mb-[1px] rounded-md border border-[#243449] bg-[#0C1626] p-2 text-[#94A3B8] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8]"
            >
              <ArrowDownWideNarrow
                className={`h-4 w-4 transition-transform ${order === 'asc' ? 'rotate-180' : ''}`}
              />
            </button>
          </div>
        </div>
      </section>

      {loading && <LoadingState message="Searching NASA PSI investigation metadata..." />}

      {!loading && error && <ErrorState message={error} onRetry={reload} />}

      {!loading && !error && data && (
        <>
          <div className="flex flex-wrap items-center justify-between gap-2 font-mono text-[11px] text-[#64748B]">
            <span>
              {formatNumber(data.pagination.total_items)} investigations match the current
              filters
            </span>
            {data.generated_at_utc && (
              <span>Inventory generated {data.generated_at_utc.slice(0, 10)}</span>
            )}
          </div>

          {data.items.length === 0 ? (
            <EmptyState
              icon={Search}
              title="No investigations match"
              description="No NASA PSI investigation in the current inventory matches these search terms and filters. Adjust the query or clear the filters to browse all 26 records."
              actionText="Clear filters"
              onAction={resetFilters}
            />
          ) : (
            <>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {data.items.map((investigation) => (
                  <InvestigationCard
                    key={investigation.investigation_id}
                    investigation={investigation}
                    onViewDetails={(id) => navigate(`/investigations/${id}`)}
                  />
                ))}
              </div>
              <Pagination
                pagination={data.pagination}
                onPageChange={(value) => {
                  setPage(value);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
              />
            </>
          )}
        </>
      )}
    </div>
  );
};

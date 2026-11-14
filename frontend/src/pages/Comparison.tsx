import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowLeftRight,
  Database,
  Download,
  ExternalLink,
  FileText,
  FlaskConical,
  Scale,
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Panel } from '../components/common/Panel';
import { FilterSelect } from '../components/common/FilterSelect';
import { Badge } from '../components/common/Badge';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { useApi } from '../hooks/useApi';
import { getComparison, getInvestigations } from '../services/api';
import { ComparedInvestigation } from '../types';
import { formatBytes, formatDateRange, formatNumber } from '../utils/format';

const MISSING = 'Not provided in NASA PSI metadata';

const ComparisonRow: React.FC<{
  label: string;
  left: React.ReactNode;
  right: React.ReactNode;
}> = ({ label, left, right }) => (
  <tr className="border-b border-[#243449]/50 last:border-b-0">
    <th
      scope="row"
      className="w-1/4 px-3 py-2.5 text-left align-top font-mono text-[10px] uppercase tracking-wider text-[#64748B]"
    >
      {label}
    </th>
    <td className="w-[37.5%] px-3 py-2.5 align-top text-xs leading-relaxed text-[#F4F7FB]">
      {left}
    </td>
    <td className="w-[37.5%] px-3 py-2.5 align-top text-xs leading-relaxed text-[#F4F7FB]">
      {right}
    </td>
  </tr>
);

const ComparisonHeader: React.FC<{ investigation: ComparedInvestigation }> = ({
  investigation,
}) => (
  <div className="rounded-lg border border-[#243449] bg-[#0C1626]/60 p-4">
    <div className="mb-1 flex items-center justify-between gap-2">
      <Badge tone="cyan">{investigation.investigation_id}</Badge>
      <Link
        to={`/investigations/${investigation.investigation_id}`}
        className="inline-flex items-center gap-1 text-[11px] font-medium text-[#35C6E8] hover:text-[#F4F7FB]"
      >
        Details <ExternalLink className="h-3 w-3" />
      </Link>
    </div>
    <p className="text-sm font-semibold leading-snug text-[#F4F7FB]">{investigation.title}</p>
    <p className="mt-1 font-mono text-[11px] text-[#FF914D]">
      {investigation.acronym ?? 'No acronym'}
    </p>
  </div>
);

const ComparisonResult: React.FC<{ a: string; b: string }> = ({ a, b }) => {
  const { data, loading, error, reload } = useApi(() => getComparison(a, b), [a, b]);

  if (loading) return <LoadingState message="Comparing metadata and file inventories..." />;
  if (error || !data) {
    return <ErrorState message={error ?? 'Comparison failed.'} onRetry={reload} />;
  }

  const [left, right] = data.investigations;
  const deltas = data.inventory_deltas;

  const deltaText = (key: string, formatter: (value: number) => string) => {
    const delta = deltas[key];
    if (!delta) return '—';
    const sign = delta.difference > 0 ? '+' : delta.difference < 0 ? '−' : '';
    return `${sign}${formatter(Math.abs(delta.difference))}`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3 rounded-lg border border-amber-400/25 bg-amber-400/5 p-4">
        <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-300" />
        <div>
          <p className="text-sm font-medium text-[#F4F7FB]">
            Metadata and file-inventory comparison only
          </p>
          <p className="mt-0.5 text-xs leading-relaxed text-[#94A3B8]">{data.notice}</p>
          <p className="mt-1 font-mono text-[10px] uppercase tracking-wider text-amber-300/80">
            Measurement comparison available: {data.measurement_comparison_available ? 'yes' : 'no'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_auto_1fr] md:items-center">
        <ComparisonHeader investigation={left} />
        <div className="hidden justify-center md:flex">
          <ArrowLeftRight className="h-5 w-5 text-[#64748B]" />
        </div>
        <ComparisonHeader investigation={right} />
      </div>

      <Panel title="Metadata comparison" icon={Database}>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-[#243449]">
                <th className="px-3 py-2 text-left font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                  Field
                </th>
                <th className="px-3 py-2 text-left font-mono text-[10px] uppercase tracking-wider text-[#35C6E8]">
                  {left.investigation_id}
                </th>
                <th className="px-3 py-2 text-left font-mono text-[10px] uppercase tracking-wider text-[#FF914D]">
                  {right.investigation_id}
                </th>
              </tr>
            </thead>
            <tbody>
              <ComparisonRow label="Title" left={left.title} right={right.title} />
              <ComparisonRow
                label="Acronym"
                left={left.acronym ?? MISSING}
                right={right.acronym ?? MISSING}
              />
              <ComparisonRow
                label="Research area"
                left={`${left.research_area ?? MISSING}${
                  left.sub_research_area ? ` · ${left.sub_research_area}` : ''
                }`}
                right={`${right.research_area ?? MISSING}${
                  right.sub_research_area ? ` · ${right.sub_research_area}` : ''
                }`}
              />
              <ComparisonRow
                label="Project type"
                left={left.project_type ?? MISSING}
                right={right.project_type ?? MISSING}
              />
              <ComparisonRow
                label="Flight platform"
                left={left.flight_platform ?? MISSING}
                right={right.flight_platform ?? MISSING}
              />
              <ComparisonRow
                label="Experiment hardware"
                left={left.experiment_hardware?.name ?? MISSING}
                right={right.experiment_hardware?.name ?? MISSING}
              />
              <ComparisonRow
                label="NASA center"
                left={left.managing_nasa_center ?? MISSING}
                right={right.managing_nasa_center ?? MISSING}
              />
              <ComparisonRow
                label="Sponsoring agency"
                left={left.sponsoring_agency ?? MISSING}
                right={right.sponsoring_agency ?? MISSING}
              />
              <ComparisonRow
                label="Flight window"
                left={formatDateRange(left.start_date_iso, left.end_date_iso)}
                right={formatDateRange(right.start_date_iso, right.end_date_iso)}
              />
              <ComparisonRow
                label="DOI"
                left={left.doi ?? MISSING}
                right={right.doi ?? MISSING}
              />
              <ComparisonRow
                label="Audit level"
                left={left.file_inventory_available ? 'Full file inventory' : 'Description only'}
                right={
                  right.file_inventory_available ? 'Full file inventory' : 'Description only'
                }
              />
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel
        title="Objectives and approach"
        subtitle="Verbatim metadata text, not measurement results"
        icon={FileText}
      >
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          {[left, right].map((investigation) => (
            <div key={investigation.investigation_id} className="space-y-4">
              <div className="flex items-center gap-2">
                <Badge tone={investigation.investigation_id === left.investigation_id ? 'cyan' : 'orange'}>
                  {investigation.investigation_id}
                </Badge>
                <span className="truncate text-xs font-medium text-[#F4F7FB]">
                  {investigation.acronym ?? investigation.title}
                </span>
              </div>
              {(
                [
                  ['Objectives', investigation.objectives],
                  ['Approach', investigation.approach],
                  ['Hypothesis', investigation.hypothesis],
                  ['Research impacts', investigation.research_impacts],
                ] as Array<[string, string | null | undefined]>
              ).map(([heading, text]) => (
                <div key={heading}>
                  <h4 className="mb-1 font-mono text-[10px] uppercase tracking-wider text-[#35C6E8]">
                    {heading}
                  </h4>
                  <p className="whitespace-pre-line text-xs leading-relaxed text-[#94A3B8]">
                    {text ?? MISSING}
                  </p>
                </div>
              ))}
            </div>
          ))}
        </div>
      </Panel>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel title="Inventory comparison" icon={Download}>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-[#243449]">
                  <th className="px-2 py-2 text-left font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                    Metric
                  </th>
                  <th className="px-2 py-2 text-right font-mono text-[10px] uppercase tracking-wider text-[#35C6E8]">
                    {left.investigation_id}
                  </th>
                  <th className="px-2 py-2 text-right font-mono text-[10px] uppercase tracking-wider text-[#FF914D]">
                    {right.investigation_id}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#243449]/50">
                {[
                  ['Derived file groups', left.dataset_count, right.dataset_count],
                  ['Files discovered', left.file_count, right.file_count],
                  [
                    'Remote inventory',
                    left.storage?.remote_inventory_size_human ?? formatBytes(0),
                    right.storage?.remote_inventory_size_human ?? formatBytes(0),
                  ],
                  [
                    'Local downloaded',
                    left.storage?.local_downloaded_size_human ?? '0 B',
                    right.storage?.local_downloaded_size_human ?? '0 B',
                  ],
                  [
                    'Pending download',
                    left.storage?.pending_download_size_human ?? '0 B',
                    right.storage?.pending_download_size_human ?? '0 B',
                  ],
                  [
                    'Over size limit',
                    left.storage?.over_limit_size_human ?? '0 B',
                    right.storage?.over_limit_size_human ?? '0 B',
                  ],
                ].map(([label, leftValue, rightValue]) => (
                  <tr key={String(label)}>
                    <td className="px-2 py-2 font-mono text-[11px] text-[#94A3B8]">{label}</td>
                    <td className="px-2 py-2 text-right font-mono text-xs text-[#F4F7FB]">
                      {typeof leftValue === 'number' ? formatNumber(leftValue) : leftValue}
                    </td>
                    <td className="px-2 py-2 text-right font-mono text-xs text-[#F4F7FB]">
                      {typeof rightValue === 'number' ? formatNumber(rightValue) : rightValue}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-[10px] text-[#64748B]">
            Local downloaded storage is shown separately because the audit downloaded no
            files.
          </p>
        </Panel>

        <Panel title="Inventory deltas" subtitle="Left minus right" icon={Scale}>
          <div className="space-y-2">
            {(
              [
                { label: 'File count', key: 'file_count', formatter: (value: number) => formatNumber(value) },
                { label: 'Derived groups', key: 'dataset_count', formatter: (value: number) => formatNumber(value) },
                {
                  label: 'Remote inventory',
                  key: 'remote_inventory_size_bytes',
                  formatter: (value: number) => formatBytes(value),
                },
              ] as Array<{ label: string; key: string; formatter: (value: number) => string }>
            ).map(({ label, key, formatter }) => (
              <div
                key={key}
                className="flex items-center justify-between gap-3 rounded-md border border-[#243449]/70 bg-[#0C1626]/50 px-3 py-2"
              >
                <span className="font-mono text-[11px] text-[#94A3B8]">{label}</span>
                <span className="font-mono text-sm font-semibold text-[#F4F7FB]">
                  {deltaText(key, formatter)}
                </span>
              </div>
            ))}
          </div>
          {data.shared_keywords.length > 0 && (
            <div className="mt-4 border-t border-[#243449]/60 pt-3">
              <p className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                Shared keywords
              </p>
              <div className="flex flex-wrap gap-1.5">
                {data.shared_keywords.map((keyword) => (
                  <Badge key={keyword} tone="purple">
                    {keyword}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel title="Format overlap" subtitle="Counts by format category" icon={Database}>
          {Object.keys(data.format_overlap).length > 0 ? (
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-[#243449]">
                  <th className="px-2 py-2 text-left font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                    Category
                  </th>
                  <th className="px-2 py-2 text-right font-mono text-[10px] uppercase tracking-wider text-[#35C6E8]">
                    {left.investigation_id}
                  </th>
                  <th className="px-2 py-2 text-right font-mono text-[10px] uppercase tracking-wider text-[#FF914D]">
                    {right.investigation_id}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#243449]/50">
                {Object.entries(data.format_overlap).map(([category, counts]) => (
                  <tr key={category}>
                    <td className="px-2 py-2 text-xs capitalize text-[#94A3B8]">{category}</td>
                    <td className="px-2 py-2 text-right font-mono text-xs text-[#F4F7FB]">
                      {formatNumber(counts[left.investigation_id] ?? 0)}
                    </td>
                    <td className="px-2 py-2 text-right font-mono text-xs text-[#F4F7FB]">
                      {formatNumber(counts[right.investigation_id] ?? 0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-[#64748B]">
              At least one investigation has no audited format inventory.
            </p>
          )}
        </Panel>

        <Panel title="Experimental measurements" icon={FlaskConical}>
          <div className="flex items-start gap-3 rounded-md border border-dashed border-[#243449] bg-[#0C1626]/40 p-4">
            <FlaskConical className="mt-0.5 h-4 w-4 flex-shrink-0 text-[#64748B]" />
            <div>
              <p className="text-sm font-medium text-[#F4F7FB]">
                Measurement comparison is not available
              </p>
              <p className="mt-1 text-xs leading-relaxed text-[#94A3B8]">
                FlameLens has not downloaded, parsed, or integrated any experimental
                measurement datasets from these investigations. This screen therefore
                compares metadata and file inventories only. No scientific comparability or
                numerical equivalence is implied.
              </p>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
};

export const Comparison: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [left, setLeft] = useState(searchParams.get('a') ?? '');
  const [right, setRight] = useState(searchParams.get('b') ?? '');

  const investigations = useApi(
    () => getInvestigations({ page_size: 100, sort_by: 'id', order: 'asc' }),
    []
  );

  const updateParams = (nextLeft: string, nextRight: string) => {
    const next = new URLSearchParams();
    if (nextLeft) next.set('a', nextLeft);
    if (nextRight) next.set('b', nextRight);
    setSearchParams(next, { replace: true });
  };

  const changeLeft = (value: string) => {
    setLeft(value);
    updateParams(value, right);
  };
  const changeRight = (value: string) => {
    setRight(value);
    updateParams(left, value);
  };
  const swap = () => {
    setLeft(right);
    setRight(left);
    updateParams(right, left);
  };
  const clear = () => {
    setLeft('');
    setRight('');
    updateParams('', '');
  };

  const options = (investigations.data?.items ?? []).map((item) => ({
    value: item.investigation_id,
    label: `${item.investigation_id} · ${item.acronym ?? item.title.slice(0, 38)}`,
  }));

  const sameSelection = Boolean(left) && left === right;
  const ready = Boolean(left) && Boolean(right) && !sameSelection;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Comparison Studio"
        subtitle="Compare NASA PSI metadata, scientific descriptions, and file inventories for two investigations. Measurement-level comparison is explicitly out of scope."
        badge="Metadata only"
      />

      <section className="rounded-lg border border-[#243449] bg-[#111E30] p-5">
        <div className="grid grid-cols-1 items-end gap-3 md:grid-cols-[1fr_auto_1fr_auto]">
          <FilterSelect
            label="Investigation A"
            value={left}
            onChange={changeLeft}
            options={options}
            allLabel="Select an investigation"
          />
          <button
            onClick={swap}
            disabled={!left && !right}
            title="Swap investigations"
            className="mb-[1px] inline-flex items-center justify-center rounded-md border border-[#243449] bg-[#0C1626] p-2 text-[#94A3B8] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8] disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ArrowLeftRight className="h-4 w-4" />
          </button>
          <FilterSelect
            label="Investigation B"
            value={right}
            onChange={changeRight}
            options={options}
            allLabel="Select an investigation"
          />
          <button
            onClick={clear}
            disabled={!left && !right}
            className="mb-[1px] rounded-md border border-[#243449] bg-[#0C1626] px-3 py-2 text-xs font-medium text-[#94A3B8] transition-colors hover:border-[#FF914D] hover:text-[#FF914D] disabled:cursor-not-allowed disabled:opacity-40"
          >
            Clear
          </button>
        </div>
        {investigations.error && (
          <p className="mt-3 text-xs text-rose-300">{investigations.error}</p>
        )}
        {sameSelection && (
          <p className="mt-3 text-xs text-amber-300">
            Select two different investigations to compare.
          </p>
        )}
      </section>

      {!ready && (
        <div className="rounded-lg border border-dashed border-[#243449] bg-[#0C1626]/40 p-10 text-center">
          <Scale className="mx-auto mb-3 h-8 w-8 text-[#35C6E8]" />
          <h3 className="mb-1 text-base font-semibold text-[#F4F7FB]">
            Select two investigations
          </h3>
          <p className="mx-auto max-w-xl text-sm text-[#94A3B8]">
            Choose investigation A and investigation B to compare metadata, objectives,
            research approach, available experimental parameters, and file inventories.
            Numerical measurement comparison is not available because no measurements have
            been parsed.
          </p>
        </div>
      )}

      {ready && <ComparisonResult a={left} b={right} />}
    </div>
  );
};

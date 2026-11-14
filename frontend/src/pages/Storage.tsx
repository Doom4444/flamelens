import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  Cloud,
  Database,
  Download,
  FolderTree,
  HardDrive,
  ShieldCheck,
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Panel } from '../components/common/Panel';
import { StatCard } from '../components/common/StatCard';
import { DonutChart } from '../components/common/DonutChart';
import { BarChart } from '../components/common/BarChart';
import { Badge } from '../components/common/Badge';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { useApi } from '../hooks/useApi';
import { getStorageAnalytics } from '../services/api';
import { capitalize, formatBytes, formatNumber } from '../utils/format';

export const Storage: React.FC = () => {
  const navigate = useNavigate();
  const { data, loading, error, reload } = useApi(getStorageAnalytics, []);

  if (loading) {
    return (
      <div>
        <PageHeader
          title="Storage Analytics"
          subtitle="Remote NASA PSI inventory size versus local FlameLens storage."
          badge="Storage"
        />
        <LoadingState message="Calculating storage analytics..." />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div>
        <PageHeader
          title="Storage Analytics"
          subtitle="Remote NASA PSI inventory size versus local FlameLens storage."
          badge="Storage"
        />
        <ErrorState message={error ?? 'Storage analytics are unavailable.'} onRetry={reload} />
      </div>
    );
  }

  const { global } = data;
  const totalFiles = global.file_counts?.current_files ?? 0;
  const remoteTotal = global.remote_inventory_size_bytes || 1;

  const categorySlices = data.format_category_distribution.map((row) => ({
    label: capitalize(row.format_category),
    value: row.count,
  }));

  const investigationBars = [...data.investigations]
    .sort(
      (a, b) =>
        (b.storage.remote_inventory_size_bytes ?? 0) -
        (a.storage.remote_inventory_size_bytes ?? 0)
    )
    .map((row) => ({
      label: `${row.investigation_id} · ${row.acronym ?? row.title.slice(0, 24)}`,
      value: row.storage.remote_inventory_size_bytes,
      valueLabel: row.storage.remote_inventory_size_human ?? formatBytes(row.storage.remote_inventory_size_bytes),
      hint: `${formatNumber(row.file_counts?.total_discovered ?? 0)} files · ${(
        row.storage.share_of_remote_bytes ?? 0
      ).toFixed(1)}% of audited remote bytes`,
    }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Storage Analytics"
        subtitle="Remote inventory size is what NASA PSI reports for its files. Local downloaded storage is tracked separately and remains 0 B in this prototype."
        badge="Remote vs local"
        action={<Badge tone="orange">0 B downloaded locally</Badge>}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatCard
          label="Remote inventory size"
          value={global.remote_inventory_size_human ?? formatBytes(remoteTotal)}
          description={`PSI reports ${global.psi_reported_total_file_size_human ?? 'an unreconciled total'}`}
          icon={Cloud}
          accentColor="cyan"
        />
        <StatCard
          label="Local downloaded storage"
          value={global.local_downloaded_size_human ?? '0 B'}
          description={`${formatNumber(global.file_counts?.downloaded_files ?? 0)} files downloaded`}
          icon={HardDrive}
          accentColor="orange"
        />
        <StatCard
          label="Eligible · pending download"
          value={formatNumber(global.pending_download_file_count)}
          description={`${global.pending_download_size_human ?? '0 B'} within the 100 MiB limit`}
          icon={Download}
          accentColor="blue"
        />
        <StatCard
          label="Over size limit"
          value={formatNumber(global.over_limit_file_count)}
          description={`${global.over_limit_size_human ?? '0 B'} never auto-downloaded`}
          icon={AlertTriangle}
          accentColor="orange"
        />
        <StatCard
          label="Historical removed"
          value={formatNumber(global.file_counts?.historical_removed_files ?? 0)}
          description={`${formatBytes(global.file_counts?.historical_removed_total_size_bytes)} removed upstream, audit preserved`}
          icon={FolderTree}
          accentColor="purple"
        />
        <StatCard
          label="Audited coverage"
          value={`${global.investigations_with_file_inventory} / ${global.investigations_discovered}`}
          description={`${global.investigations_without_file_inventory} investigations are metadata-only`}
          icon={Database}
          accentColor="cyan"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel
          title="Format categories"
          subtitle={`${formatNumber(totalFiles)} current files · remote counts`}
          icon={FolderTree}
        >
          <DonutChart
            data={categorySlices}
            centerLabel="FILES"
            centerValue={formatNumber(totalFiles)}
          />
        </Panel>
        <Panel
          title="Remote size by investigation"
          subtitle="Audited investigations only — click to open details"
          icon={Cloud}
        >
          <BarChart
            data={investigationBars}
            onSelect={(item) => {
              const id = item.label.split(' · ')[0];
              navigate(`/investigations/${id}`);
            }}
          />
          <p className="mt-3 text-[11px] text-[#64748B]">
            Shares are computed against the {global.remote_inventory_size_human} audited
            remote inventory. They do not represent local disk usage.
          </p>
        </Panel>
      </div>

      <Panel
        title="Investigation storage ledger"
        subtitle="Separate columns for remote inventory and local storage"
        icon={Database}
      >
        <div className="overflow-x-auto">
          <table className="min-w-full text-left">
            <thead className="border-b border-[#243449]">
              <tr>
                {[
                  'Investigation',
                  'Groups',
                  'Files',
                  'Remote size',
                  'Share',
                  'Eligible',
                  'Over limit',
                  'Local',
                ].map((header) => (
                  <th
                    key={header}
                    className={`whitespace-nowrap px-3 py-2.5 font-mono text-[10px] uppercase tracking-wider text-[#64748B] ${
                      ['Groups', 'Files', 'Eligible', 'Over limit'].includes(header)
                        ? 'text-right'
                        : 'text-left'
                    }`}
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#243449]/60">
              {data.investigations.map((row) => (
                <tr key={row.investigation_id} className="hover:bg-[#0C1626]/40">
                  <td className="px-3 py-2.5">
                    <Link
                      to={`/investigations/${row.investigation_id}`}
                      className="font-mono text-xs text-[#35C6E8] hover:text-[#F4F7FB]"
                    >
                      {row.investigation_id}
                    </Link>
                    <p className="max-w-[18rem] truncate text-[11px] text-[#94A3B8]">
                      {row.acronym ? `${row.acronym} · ` : ''}
                      {row.title}
                    </p>
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono text-xs text-[#F4F7FB]">
                    {formatNumber(row.dataset_count)}
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono text-xs text-[#F4F7FB]">
                    {formatNumber(row.file_counts?.total_discovered ?? 0)}
                  </td>
                  <td className="whitespace-nowrap px-3 py-2.5 font-mono text-xs text-[#35C6E8]">
                    {row.storage.remote_inventory_size_human ??
                      formatBytes(row.storage.remote_inventory_size_bytes)}
                  </td>
                  <td className="px-3 py-2.5 font-mono text-[11px] text-[#94A3B8]">
                    {(row.storage.share_of_remote_bytes ?? 0).toFixed(1)}%
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono text-xs text-amber-300">
                    {formatNumber(row.file_counts?.pending_download ?? 0)}
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono text-xs text-rose-300">
                    {formatNumber(row.file_counts?.over_limit ?? 0)}
                  </td>
                  <td className="whitespace-nowrap px-3 py-2.5 font-mono text-xs text-[#FF914D]">
                    {row.storage.local_downloaded_size_human ?? '0 B'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel
          title="Without audited file inventory"
          subtitle="Metadata-only records — no file or storage claims are made"
          icon={Database}
        >
          <div className="flex flex-wrap gap-2">
            {data.investigations_without_file_inventory.map((row) => (
              <Link
                key={row.investigation_id}
                to={`/investigations/${row.investigation_id}`}
                title={row.title}
                className="rounded border border-[#243449] bg-[#0C1626] px-2 py-1 font-mono text-[11px] text-[#94A3B8] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8]"
              >
                {row.investigation_id}
              </Link>
            ))}
          </div>
          <p className="mt-3 text-[11px] leading-relaxed text-[#64748B]">
            NASA PSI exposes their metadata, but the Stage 1 audit did not enumerate their
            files. They are intentionally excluded from storage totals.
          </p>
        </Panel>

        <Panel title="Download policy" subtitle="Applied by the Stage 1 audit" icon={ShieldCheck}>
          <dl className="space-y-2 text-xs">
            <div className="flex items-center justify-between gap-3 border-b border-[#243449]/60 pb-2">
              <dt className="text-[#94A3B8]">Maximum automatic file size</dt>
              <dd className="font-mono text-[#F4F7FB]">
                {String(data.download_policy.max_file_size_mb ?? 100)} MiB
              </dd>
            </div>
            <div className="flex items-center justify-between gap-3 border-b border-[#243449]/60 pb-2">
              <dt className="text-[#94A3B8]">Bytes limit</dt>
              <dd className="font-mono text-[#F4F7FB]">
                {formatNumber(Number(data.download_policy.max_file_size_bytes ?? 104857600))} B
              </dd>
            </div>
            <div className="flex items-center justify-between gap-3 border-b border-[#243449]/60 pb-2">
              <dt className="text-[#94A3B8]">Environment variable</dt>
              <dd className="font-mono text-[#F4F7FB]">
                {String(data.download_policy.environment_variable ?? 'MAX_FILE_SIZE_MB')}
              </dd>
            </div>
          </dl>
          <p className="mt-3 text-[11px] leading-relaxed text-[#94A3B8]">
            {String(
              data.download_policy.note ??
                'Sizes above the limit are inventoried but never downloaded automatically.'
            )}
          </p>
          <p className="mt-2 text-[10px] font-mono text-[#64748B]">
            Units: {data.units?.byte_conversion ?? 'binary units'}
          </p>
        </Panel>
      </div>

      <Panel
        title="Audited data gaps"
        subtitle="Known limitations in the NASA PSI file listings"
        icon={AlertTriangle}
      >
        <div className="space-y-3">
          {data.data_gaps.map((gap) => (
            <div
              key={gap.id}
              className="rounded-md border border-amber-400/20 bg-amber-400/5 p-3"
            >
              <div className="mb-1 flex flex-wrap items-center gap-2">
                <Badge tone={gap.severity === 'high' ? 'red' : 'amber'}>
                  {gap.severity.toUpperCase()}
                </Badge>
                <span className="font-mono text-[11px] text-[#94A3B8]">
                  {gap.id} · {gap.investigation_id}
                </span>
              </div>
              <p className="text-xs font-medium text-[#F4F7FB]">{gap.summary}</p>
              <p className="mt-1 text-[11px] leading-relaxed text-[#94A3B8]">{gap.details}</p>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
};

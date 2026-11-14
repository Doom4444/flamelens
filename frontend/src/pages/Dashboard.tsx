import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowRight,
  Cloud,
  Database,
  Download,
  FolderSearch,
  HardDrive,
  Layers,
  ShieldCheck,
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { StatCard } from '../components/common/StatCard';
import { Panel } from '../components/common/Panel';
import { DonutChart } from '../components/common/DonutChart';
import { BarChart } from '../components/common/BarChart';
import { InvestigationCard } from '../components/common/InvestigationCard';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { Badge } from '../components/common/Badge';
import { useApi } from '../hooks/useApi';
import { getOverview } from '../services/api';
import {
  capitalize,
  formatBytes,
  formatDate,
  formatNumber,
} from '../utils/format';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data, loading, error, reload } = useApi(getOverview, []);

  if (loading) {
    return (
      <div>
        <PageHeader
          title="Research Overview"
          subtitle="Live dashboard over the audited NASA PSI combustion investigation inventories."
          badge="Live metadata"
        />
        <LoadingState message="Loading overview analytics..." />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div>
        <PageHeader
          title="Research Overview"
          subtitle="Live dashboard over the audited NASA PSI combustion investigation inventories."
          badge="Live metadata"
        />
        <ErrorState
          message={error ?? 'Overview data is unavailable.'}
          onRetry={reload}
        />
      </div>
    );
  }

  const { totals } = data;
  const formatSlices = data.format_category_distribution.map((row) => ({
    label: capitalize(row.format_category),
    value: row.count,
  }));
  const extensionBars = data.file_type_distribution.slice(0, 9).map((row) => ({
    label: row.extension,
    value: row.count,
    valueLabel: `${formatNumber(row.count)} files`,
    hint: `${row.size_human ?? formatBytes(row.size_bytes)} remote · ${row.share_of_bytes}% of bytes`,
  }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Research Overview"
        subtitle="Live statistics computed from the audited NASA PSI inventories. Remote inventory size is never presented as local storage."
        badge="Live metadata"
        action={
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => navigate('/files')}
              className="inline-flex items-center gap-2 rounded-md border border-[#243449] bg-[#111E30] px-3 py-2 text-xs font-medium text-[#F4F7FB] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8]"
            >
              <FolderSearch className="h-3.5 w-3.5" />
              File explorer
            </button>
            <button
              onClick={() => navigate('/storage')}
              className="inline-flex items-center gap-2 rounded-md border border-[#35C6E8]/40 bg-[#35C6E8]/10 px-3 py-2 text-xs font-medium text-[#35C6E8] transition-colors hover:bg-[#35C6E8]/20"
            >
              <HardDrive className="h-3.5 w-3.5" />
              Storage analytics
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatCard
          label="Investigations"
          value={formatNumber(totals.investigations)}
          description={`${totals.investigations_with_file_inventory} with audited file inventory`}
          icon={Database}
          accentColor="cyan"
        />
        <StatCard
          label="Discovered files"
          value={formatNumber(totals.files)}
          description={`${formatNumber(totals.download_eligible_files)} within limit · ${formatNumber(
            totals.over_limit_files
          )} over limit`}
          icon={Download}
          accentColor="blue"
        />
        <StatCard
          label="Derived file groups"
          value={formatNumber(totals.dataset_groups)}
          description="FlameLens-derived, not NASA dataset IDs"
          icon={Layers}
          accentColor="purple"
        />
        <StatCard
          label="Remote inventory size"
          value={totals.remote_inventory_size_human ?? formatBytes(totals.remote_inventory_size_bytes)}
          description={`PSI reports ${totals.psi_reported_total_file_size_human ?? 'an unreconciled total'}`}
          icon={Cloud}
          accentColor="cyan"
        />
        <StatCard
          label="Downloaded local storage"
          value={totals.local_downloaded_size_human ?? '0 B'}
          description="No scientific files downloaded in this prototype"
          icon={HardDrive}
          accentColor="orange"
        />
        <StatCard
          label="Historical removed files"
          value={formatNumber(totals.historical_removed_files)}
          description={`${totals.data_gap_count} audited data gaps recorded`}
          icon={AlertTriangle}
          accentColor="orange"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel
          title="File type distribution"
          subtitle="Current inventory grouped by format category"
          icon={Layers}
          action={<Badge tone="cyan">Derived from 1,520 files</Badge>}
        >
          <DonutChart
            data={formatSlices}
            centerLabel="FILES"
            centerValue={formatNumber(totals.files)}
          />
        </Panel>

        <Panel
          title="Extensions by file count"
          subtitle="Top formats across the audited inventories"
          icon={FolderSearch}
          action={
            <button
              onClick={() => navigate('/files')}
              className="inline-flex items-center gap-1 text-xs font-medium text-[#35C6E8] hover:text-[#F4F7FB]"
            >
              Explore files <ArrowRight className="h-3 w-3" />
            </button>
          }
        >
          <BarChart data={extensionBars} />
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Panel
          title="Research areas"
          subtitle="Click a bar to filter the investigation explorer"
          icon={Database}
          className="lg:col-span-2"
        >
          <BarChart
            data={data.research_area_distribution.map((row) => ({
              label: row.research_area,
              value: row.investigation_count,
              valueLabel: `${row.investigation_count} investigations`,
              hint: `${row.with_file_inventory} with audited file inventory`,
              tone: 'purple',
            }))}
            onSelect={(item) =>
              navigate(`/investigations?research_area=${encodeURIComponent(item.label)}`)
            }
          />
        </Panel>

        <Panel title="Download status" subtitle="Remote inventory only" icon={Download}>
          <ul className="space-y-2.5">
            {data.download_status_distribution.map((row) => (
              <li
                key={row.download_status}
                className="flex items-center justify-between gap-3 rounded-md border border-[#243449]/70 bg-[#0C1626]/50 px-3 py-2"
              >
                <div>
                  <p className="font-mono text-xs text-[#F4F7FB]">{row.download_status}</p>
                  <p className="text-[10px] text-[#64748B]">
                    {row.size_human ?? formatBytes(row.size_bytes)} remote
                  </p>
                </div>
                <span className="font-mono text-sm font-semibold text-[#35C6E8]">
                  {formatNumber(row.count)}
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-[11px] leading-relaxed text-[#64748B]">
            PENDING means eligible for a future controlled download; no file is claimed
            to be local.
          </p>
        </Panel>
      </div>

      <Panel
        title="Featured investigations"
        subtitle="Audited investigations, largest remote inventories first"
        icon={Database}
        action={
          <button
            onClick={() => navigate('/investigations')}
            className="inline-flex items-center gap-1 text-xs font-medium text-[#35C6E8] hover:text-[#F4F7FB]"
          >
            All investigations <ArrowRight className="h-3 w-3" />
          </button>
        }
      >
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data.featured_investigations.slice(0, 3).map((investigation) => (
            <InvestigationCard
              key={investigation.investigation_id}
              investigation={investigation}
              onViewDetails={(id) => navigate(`/investigations/${id}`)}
            />
          ))}
        </div>
      </Panel>

      <Panel
        title="Scientific integrity notes"
        subtitle="How to read these numbers"
        icon={ShieldCheck}
      >
        <ul className="space-y-2">
          {data.data_notes.map((note) => (
            <li key={note} className="flex gap-2 text-xs leading-relaxed text-[#94A3B8]">
              <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-[#35C6E8]" />
              {note}
            </li>
          ))}
        </ul>
        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-1 border-t border-[#243449]/60 pt-3 font-mono text-[10px] text-[#64748B]">
          <span>Source: {data.data_source}</span>
          <span>Inventory generated: {formatDate(data.generated_at_utc)}</span>
          <span>PSI snapshot: {formatDate(data.snapshot_captured_at_utc)}</span>
        </div>
      </Panel>
    </div>
  );
};

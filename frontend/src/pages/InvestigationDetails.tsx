import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowLeft,
  Building2,
  Calendar,
  Cloud,
  Database,
  Download,
  ExternalLink,
  FileText,
  FolderSearch,
  FolderTree,
  HardDrive,
  Link2,
  Rocket,
  Scale,
  ShieldCheck,
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Panel } from '../components/common/Panel';
import { Badge, downloadStatusTone, downloadStatusLabel } from '../components/common/Badge';
import { DonutChart } from '../components/common/DonutChart';
import { BarChart } from '../components/common/BarChart';
import { FileTable } from '../components/common/FileTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { useApi } from '../hooks/useApi';
import { exportUrl, getInvestigation, getInvestigationFiles } from '../services/api';
import {
  capitalize,
  formatBytes,
  formatDate,
  formatDateRange,
  formatNumber,
} from '../utils/format';

const InfoRow: React.FC<{ label: string; children: React.ReactNode }> = ({
  label,
  children,
}) => (
  <div className="border-b border-[#243449]/50 py-2 last:border-b-0">
    <dt className="font-mono text-[10px] uppercase tracking-wider text-[#64748B]">{label}</dt>
    <dd className="mt-0.5 text-xs leading-relaxed text-[#F4F7FB]">{children}</dd>
  </div>
);

const DescriptionSection: React.FC<{
  heading: string;
  text?: string | null;
}> = ({ heading, text }) =>
  text ? (
    <div>
      <h3 className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-[#35C6E8]">
        {heading}
      </h3>
      <p className="whitespace-pre-line text-sm leading-relaxed text-[#94A3B8]">{text}</p>
    </div>
  ) : null;

export const InvestigationDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const detail = useApi(
    () => (id ? getInvestigation(id) : Promise.reject(new Error('Missing investigation id'))),
    [id]
  );
  const files = useApi(
    () =>
      id
        ? getInvestigationFiles(id, { page_size: 8, sort_by: 'size', order: 'desc' })
        : Promise.reject(new Error('Missing investigation id')),
    [id]
  );

  if (detail.loading) {
    return <LoadingState message="Loading investigation record..." />;
  }

  if (detail.error || !detail.data) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate('/investigations')}
          className="inline-flex items-center gap-1.5 font-mono text-xs text-[#94A3B8] transition-colors hover:text-[#35C6E8]"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to investigations
        </button>
        <ErrorState
          title="Investigation not available"
          message={detail.error ?? 'The investigation could not be loaded.'}
          onRetry={detail.reload}
        />
      </div>
    );
  }

  const record = detail.data;
  const storage = record.storage;
  const counts = record.file_counts ?? {};
  const description = record.description ?? {};
  const hasInventory = record.file_inventory_available;

  const formatSlices = Object.entries(record.format_category_distribution ?? {}).map(
    ([label, value]) => ({ label: capitalize(label), value })
  );
  const extensionBars = Object.entries(record.format_distribution ?? {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([label, value]) => ({
      label,
      value,
      valueLabel: `${formatNumber(value)} files`,
    }));

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/investigations')}
        className="inline-flex items-center gap-1.5 font-mono text-xs text-[#94A3B8] transition-colors hover:text-[#35C6E8]"
      >
        <ArrowLeft className="h-3.5 w-3.5" /> Back to investigations
      </button>

      <PageHeader
        title={record.title}
        subtitle={
          record.proposal_title ||
          `${record.research_area ?? 'Combustion science'} · ${
            record.flight_platform ?? 'NASA PSI'
          }`
        }
        badge={record.investigation_id}
        action={
          <div className="flex flex-wrap gap-2">
            <Link
              to={`/files?investigation=${record.investigation_id}`}
              className="inline-flex items-center gap-2 rounded-md border border-[#243449] bg-[#111E30] px-3 py-2 text-xs font-medium text-[#F4F7FB] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8]"
            >
              <FolderSearch className="h-3.5 w-3.5" /> Explore files
            </Link>
            <Link
              to={`/comparison?a=${record.investigation_id}`}
              className="inline-flex items-center gap-2 rounded-md border border-[#243449] bg-[#111E30] px-3 py-2 text-xs font-medium text-[#F4F7FB] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8]"
            >
              <Scale className="h-3.5 w-3.5" /> Compare
            </Link>
            <a
              href={exportUrl('csv', {}, record.investigation_id)}
              className="inline-flex items-center gap-2 rounded-md border border-[#35C6E8]/40 bg-[#35C6E8]/10 px-3 py-2 text-xs font-medium text-[#35C6E8] transition-colors hover:bg-[#35C6E8]/20"
            >
              <Download className="h-3.5 w-3.5" /> CSV
            </a>
            <a
              href={exportUrl('json', {}, record.investigation_id)}
              className="inline-flex items-center gap-2 rounded-md border border-[#243449] bg-[#111E30] px-3 py-2 text-xs font-medium text-[#F4F7FB] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8]"
            >
              <Download className="h-3.5 w-3.5" /> JSON
            </a>
          </div>
        }
      />

      <div className="flex flex-wrap items-center gap-2">
        {record.acronym && <Badge tone="orange">{record.acronym}</Badge>}
        {record.research_area && <Badge tone="cyan">{record.research_area}</Badge>}
        {record.sub_research_area && <Badge tone="slate">{record.sub_research_area}</Badge>}
        <Badge tone={hasInventory ? 'green' : 'slate'}>
          {hasInventory ? 'Audited file inventory' : 'Metadata only'}
        </Badge>
        {record.doi && (
          <a
            href={`https://doi.org/${record.doi}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[11px] font-mono text-[#35C6E8] hover:text-[#F4F7FB]"
          >
            <Link2 className="h-3 w-3" /> DOI {record.doi}
          </a>
        )}
      </div>

      {hasInventory && storage && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-5">
          {[
            {
              label: 'Files discovered',
              value: formatNumber(counts.total_discovered ?? record.file_count),
              sub: `${formatNumber(record.dataset_count)} derived groups`,
              icon: FileText,
            },
            {
              label: 'Remote inventory',
              value: storage.remote_inventory_size_human ?? formatBytes(storage.remote_inventory_size_bytes),
              sub: storage.remote_inventory_complete ? 'Complete per PSI' : 'Known-size subtotal',
              icon: Cloud,
            },
            {
              label: 'Local downloaded',
              value: storage.local_downloaded_size_human ?? '0 B',
              sub: 'No files stored locally',
              icon: HardDrive,
            },
            {
              label: 'Eligible · pending',
              value: formatNumber(counts.pending_download ?? 0),
              sub: storage.pending_download_size_human ?? '0 B',
              icon: Download,
            },
            {
              label: 'Over size limit',
              value: formatNumber(counts.over_limit ?? 0),
              sub: storage.over_limit_size_human ?? '0 B',
              icon: AlertTriangle,
            },
          ].map((metric) => (
            <div
              key={metric.label}
              className="rounded-lg border border-[#243449] bg-[#111E30] p-3.5"
            >
              <div className="mb-2 flex items-center justify-between">
                <span className="font-mono text-[9px] uppercase tracking-wider text-[#64748B]">
                  {metric.label}
                </span>
                <metric.icon className="h-3.5 w-3.5 text-[#35C6E8]" />
              </div>
              <p className="font-mono text-lg font-bold text-[#F4F7FB]">{metric.value}</p>
              <p className="mt-0.5 text-[10px] text-[#64748B]">{metric.sub}</p>
            </div>
          ))}
        </div>
      )}

      {!hasInventory && (
        <div className="flex items-start gap-3 rounded-lg border border-amber-400/25 bg-amber-400/5 p-4">
          <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-300" />
          <div>
            <p className="text-sm font-medium text-[#F4F7FB]">
              No audited file inventory for this investigation
            </p>
            <p className="mt-0.5 text-xs leading-relaxed text-[#94A3B8]">
              NASA PSI exposes metadata for this investigation, but the Stage 1 audit did
              not enumerate its files. FlameLens therefore shows no file counts or storage
              totals rather than inventing them.
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Panel title="Investigation metadata" icon={Database} className="lg:col-span-1">
          <dl>
            <InfoRow label="Investigation ID">{record.investigation_id}</InfoRow>
            <InfoRow label="Acronym">{record.acronym ?? '—'}</InfoRow>
            <InfoRow label="Research area">
              {record.research_area ?? '—'}
              {record.sub_research_area ? ` · ${record.sub_research_area}` : ''}
            </InfoRow>
            <InfoRow label="Project type">{record.project_type ?? '—'}</InfoRow>
            <InfoRow label="Flight platform">
              <span className="inline-flex items-center gap-1.5">
                <Rocket className="h-3 w-3 text-[#64748B]" />
                {record.flight_platform ?? '—'}
              </span>
            </InfoRow>
            <InfoRow label="Experiment hardware">
              {record.experiment_hardware?.name ?? '—'}
            </InfoRow>
            <InfoRow label="Managing NASA center">
              <span className="inline-flex items-center gap-1.5">
                <Building2 className="h-3 w-3 text-[#64748B]" />
                {record.managing_nasa_center ?? '—'}
              </span>
            </InfoRow>
            <InfoRow label="Sponsoring agency">
              {record.sponsoring_agency ?? '—'}
            </InfoRow>
            <InfoRow label="Flight window">
              <span className="inline-flex items-center gap-1.5">
                <Calendar className="h-3 w-3 text-[#64748B]" />
                {formatDateRange(record.start_date_iso, record.end_date_iso)}
              </span>
            </InfoRow>
            <InfoRow label="Audit level">
              {record.audit_level === 'full_audit' ? 'Full file inventory audit' : 'Description only'}
            </InfoRow>
          </dl>
          {record.keywords.length > 0 && (
            <div className="mt-3 border-t border-[#243449]/60 pt-3">
              <p className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                Keywords
              </p>
              <div className="flex flex-wrap gap-1.5">
                {record.keywords.map((keyword) => (
                  <Badge key={keyword} tone="slate">
                    {keyword}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </Panel>

        <Panel
          title="Scientific description"
          subtitle="Verbatim NASA PSI metadata — no measurements are inferred"
          icon={ShieldCheck}
          className="lg:col-span-2"
        >
          {description.objectives ||
          description.approach ||
          description.hypothesis ||
          description.research_impacts ? (
            <div className="space-y-5">
              <DescriptionSection heading="Objectives" text={description.objectives} />
              <DescriptionSection heading="Approach" text={description.approach} />
              <DescriptionSection heading="Hypothesis" text={description.hypothesis} />
              <DescriptionSection
                heading="Research impacts"
                text={description.research_impacts}
              />
            </div>
          ) : (
            <p className="text-sm text-[#64748B]">
              This NASA PSI record does not include a structured scientific description.
            </p>
          )}
        </Panel>
      </div>

      {hasInventory && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Panel
            title="Format categories"
            subtitle="Counts from the audited file inventory"
            icon={FolderTree}
          >
            {formatSlices.length > 0 ? (
              <DonutChart
                data={formatSlices}
                centerLabel="FILES"
                centerValue={formatNumber(counts.total_discovered ?? 0)}
              />
            ) : (
              <p className="text-sm text-[#64748B]">No format data available.</p>
            )}
          </Panel>
          <Panel title="Extensions" subtitle="File count by extension" icon={FileText}>
            <BarChart data={extensionBars} />
          </Panel>
        </div>
      )}

      {hasInventory && (
        <Panel
          title="Associated files"
          subtitle="Largest files first. Remote sizes are inventory values; local storage remains 0 B."
          icon={FolderSearch}
          action={
            <Link
              to={`/files?investigation=${record.investigation_id}`}
              className="inline-flex items-center gap-1 text-xs font-medium text-[#35C6E8] hover:text-[#F4F7FB]"
            >
              All {formatNumber(record.file_count)} files <FolderSearch className="h-3 w-3" />
            </Link>
          }
        >
          {files.loading && <LoadingState message="Loading associated files..." />}
          {!files.loading && files.error && (
            <ErrorState message={files.error} onRetry={files.reload} />
          )}
          {!files.loading && !files.error && files.data && (
            <>
              <FileTable files={files.data.items} />
              <div className="mt-3 flex flex-wrap gap-2">
                {Object.entries(files.data.totals.by_status).map(([status, count]) => (
                  <Badge key={status} tone={downloadStatusTone(status)}>
                    {downloadStatusLabel(status)}: {formatNumber(count)}
                  </Badge>
                ))}
              </div>
            </>
          )}
        </Panel>
      )}

      {record.dataset_groups.length > 0 && (
        <Panel
          title="Derived file groups"
          subtitle={`${formatNumber(record.dataset_groups.length)} groups derived from top-level filename category + PSI subcategory — not NASA dataset entities`}
          icon={Database}
        >
          <div className="max-h-96 overflow-y-auto">
            <table className="min-w-full text-left">
              <thead className="sticky top-0 border-b border-[#243449] bg-[#111E30]">
                <tr>
                  <th className="px-2 py-2 font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                    Group
                  </th>
                  <th className="px-2 py-2 font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                    Category
                  </th>
                  <th className="px-2 py-2 font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                    Subcategory
                  </th>
                  <th className="px-2 py-2 text-right font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                    Files
                  </th>
                  <th className="px-2 py-2 text-right font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                    Remote size
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#243449]/50">
                {record.dataset_groups.map((group) => (
                  <tr key={group.dataset_id} className="hover:bg-[#0C1626]/40">
                    <td className="max-w-[20rem] truncate px-2 py-2 font-mono text-xs text-[#F4F7FB]">
                      {group.name}
                    </td>
                    <td className="px-2 py-2 text-xs text-[#94A3B8]">
                      {group.top_level_category ?? '—'}
                    </td>
                    <td className="px-2 py-2 text-xs text-[#94A3B8]">
                      {group.psi_subcategory ?? '—'}
                    </td>
                    <td className="px-2 py-2 text-right font-mono text-xs text-[#F4F7FB]">
                      {formatNumber(group.file_count)}
                    </td>
                    <td className="px-2 py-2 text-right font-mono text-xs text-[#35C6E8]">
                      {formatBytes(group.total_size_bytes)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel title="Related investigations" icon={Link2}>
          {record.related_edges.length > 0 ? (
            <ul className="space-y-2">
              {record.related_edges.map((edge, index) => {
                const other =
                  edge.source === record.investigation_id ? edge.target : edge.source;
                return (
                  <li key={`${other}-${index}`}>
                    <Link
                      to={`/investigations/${other}`}
                      className="flex items-center justify-between gap-3 rounded-md border border-[#243449]/70 bg-[#0C1626]/50 px-3 py-2 transition-colors hover:border-[#35C6E8]/50"
                    >
                      <span className="font-mono text-xs text-[#35C6E8]">{other}</span>
                      <span className="truncate text-[10px] uppercase tracking-wider text-[#64748B]">
                        {edge.relationship ?? edge.type ?? 'related'}
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          ) : record.related_investigations.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {record.related_investigations.map((related) => (
                <Link
                  key={related}
                  to={`/investigations/${related}`}
                  className="rounded border border-[#243449] bg-[#0C1626] px-2 py-1 font-mono text-xs text-[#35C6E8] hover:border-[#35C6E8]"
                >
                  {related}
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[#64748B]">
              No related investigations are recorded in the NASA PSI metadata.
            </p>
          )}
        </Panel>

        <Panel title="Provenance" icon={ShieldCheck}>
          <dl>
            <InfoRow label="PSI API record">
              {record.psi_api_url ? (
                <a
                  href={record.psi_api_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[#35C6E8] hover:text-[#F4F7FB]"
                >
                  Open NASA PSI source <ExternalLink className="h-3 w-3" />
                </a>
              ) : (
                '—'
              )}
            </InfoRow>
            <InfoRow label="Data source">{record.data_source ?? 'NASA PSI'}</InfoRow>
            <InfoRow label="PSI version">{record.psi_version ?? '—'}</InfoRow>
            <InfoRow label="Snapshot SHA-256">
              <span className="break-all font-mono text-[10px] text-[#94A3B8]">
                {record.snapshot_sha256 ?? '—'}
              </span>
            </InfoRow>
            {record.reported_total_file_size_human && (
              <InfoRow label="PSI reported total file size">
                {record.reported_total_file_size_human}
                {storage?.delta_vs_reported_bytes !== null &&
                  storage?.delta_vs_reported_bytes !== undefined && (
                    <span className="ml-2 text-[10px] text-[#64748B]">
                      ({formatNumber(storage.delta_vs_reported_bytes)} B delta vs audited
                      inventory)
                    </span>
                  )}
              </InfoRow>
            )}
            <InfoRow label="Record generated">
              {formatDate(record.start_date_iso)} flight start · inventory metadata
            </InfoRow>
          </dl>
        </Panel>
      </div>

      {record.data_gaps.length > 0 && (
        <Panel
          title="Known data gaps"
          subtitle="Recorded by the Stage 1 audit — shown rather than hidden"
          icon={AlertTriangle}
        >
          <div className="space-y-3">
            {record.data_gaps.map((gap) => (
              <div
                key={`${gap.id}-${gap.investigation_id}`}
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
                <p className="mt-1.5 text-[11px] leading-relaxed text-[#64748B]">
                  <span className="text-[#FF914D]">Recommended: </span>
                  {gap.recommended_action}
                </p>
              </div>
            ))}
          </div>
        </Panel>
      )}

      {record.storage_notes.length > 0 && (
        <Panel title="Inventory notes" icon={FileText}>
          <ul className="space-y-2">
            {record.storage_notes.map((note) => (
              <li key={note} className="flex gap-2 text-xs leading-relaxed text-[#94A3B8]">
                <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-[#FF914D]" />
                {note}
              </li>
            ))}
          </ul>
        </Panel>
      )}
    </div>
  );
};

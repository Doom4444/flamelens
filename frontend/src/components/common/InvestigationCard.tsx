import React from 'react';
import { ArrowRight, Calendar, Database, FileText, HardDrive, Tag } from 'lucide-react';
import { InvestigationSummary } from '../../types';
import { formatDateRange, formatNumber } from '../../utils/format';

interface InvestigationCardProps {
  investigation: InvestigationSummary;
  onViewDetails: (id: string) => void;
}

export const InvestigationCard: React.FC<InvestigationCardProps> = ({
  investigation,
  onViewDetails,
}) => {
  const hasInventory = investigation.file_inventory_available;
  const remoteSize = investigation.storage?.remote_inventory_size_human;

  return (
    <div className="group flex h-full flex-col justify-between rounded-lg border border-[#243449] bg-[#111E30] p-5 transition-all hover:border-[#35C6E8]/60">
      <div>
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <span className="rounded border border-[#35C6E8]/25 bg-[#35C6E8]/10 px-2 py-0.5 font-mono text-[11px] font-medium text-[#35C6E8]">
            {investigation.investigation_id}
          </span>
          <span className="font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
            {investigation.research_area ?? 'NASA PSI'}
          </span>
        </div>

        <h4 className="mb-1 line-clamp-2 text-base font-semibold leading-snug text-[#F4F7FB] transition-colors group-hover:text-[#35C6E8]">
          {investigation.title}
        </h4>
        {investigation.acronym && (
          <p className="mb-3 font-mono text-xs text-[#FF914D]">{investigation.acronym}</p>
        )}

        <p className="mb-4 line-clamp-3 text-xs leading-relaxed text-[#94A3B8]">
          {investigation.description?.objectives ||
            investigation.description?.approach ||
            'No objective description is available in the NASA PSI metadata for this investigation.'}
        </p>

        <div className="mb-4 flex flex-wrap gap-x-4 gap-y-1.5 font-mono text-[11px] text-[#64748B]">
          <span className="inline-flex items-center gap-1.5">
            <Calendar className="h-3 w-3" />
            {formatDateRange(investigation.start_date_iso, investigation.end_date_iso)}
          </span>
          {investigation.flight_platform && (
            <span className="inline-flex items-center gap-1.5">
              <Tag className="h-3 w-3" />
              <span className="truncate">{investigation.flight_platform}</span>
            </span>
          )}
        </div>

        {hasInventory ? (
          <div className="grid grid-cols-3 gap-2 rounded-md border border-[#243449]/70 bg-[#0C1626]/60 p-2.5 text-center">
            <div>
              <p className="font-mono text-sm font-semibold text-[#F4F7FB]">
                {formatNumber(investigation.dataset_count)}
              </p>
              <p className="text-[10px] uppercase tracking-wide text-[#64748B]">Groups</p>
            </div>
            <div>
              <p className="font-mono text-sm font-semibold text-[#F4F7FB]">
                {formatNumber(investigation.file_count)}
              </p>
              <p className="text-[10px] uppercase tracking-wide text-[#64748B]">Files</p>
            </div>
            <div>
              <p className="font-mono text-sm font-semibold text-[#35C6E8]">
                {remoteSize ?? '—'}
              </p>
              <p className="text-[10px] uppercase tracking-wide text-[#64748B]">Remote</p>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 rounded-md border border-dashed border-[#243449] bg-[#0C1626]/40 p-2.5 text-[11px] text-[#64748B]">
            <HardDrive className="h-3.5 w-3.5 flex-shrink-0" />
            No audited file inventory yet — metadata only.
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-[#243449]/70 pt-3">
        <span className="inline-flex items-center gap-1.5 text-[10px] font-mono text-[#64748B]">
          {investigation.audit_level === 'full_audit' ? (
            <>
              <Database className="h-3 w-3" /> Full audit
            </>
          ) : (
            <>
              <FileText className="h-3 w-3" /> Description only
            </>
          )}
        </span>
        <button
          onClick={() => onViewDetails(investigation.investigation_id)}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-[#35C6E8] transition-colors hover:text-[#F4F7FB]"
        >
          View details
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
};

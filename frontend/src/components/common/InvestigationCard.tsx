import React from 'react';
import { ExternalLink, Tag, ShieldAlert, Radio, Flame, Sparkles } from 'lucide-react';
import { InvestigationPreview } from '../../types';

interface InvestigationCardProps {
  investigation: InvestigationPreview;
  onViewDetails: (id: string) => void;
}

export const InvestigationCard: React.FC<InvestigationCardProps> = ({
  investigation,
  onViewDetails,
}) => {
  const getCategoryBadge = () => {
    switch (investigation.category) {
      case 'prevention':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-[#35C6E8]/10 text-[#35C6E8] border border-[#35C6E8]/20">
            <ShieldAlert className="w-3 h-3" />
            Prevention
          </span>
        );
      case 'detection':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-sky-400/10 text-sky-400 border border-sky-400/20">
            <Radio className="w-3 h-3" />
            Detection
          </span>
        );
      case 'suppression':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-[#FF914D]/10 text-[#FF914D] border border-[#FF914D]/20">
            <Flame className="w-3 h-3" />
            Suppression
          </span>
        );
    }
  };

  return (
    <div className="flex flex-col justify-between p-5 rounded-lg bg-[#111E30] border border-[#243449] hover:border-[#35C6E8]/60 transition-all group">
      <div>
        <div className="flex items-center justify-between gap-2 mb-2">
          {getCategoryBadge()}
          {investigation.accessionId ? (
            <span className="text-[11px] font-mono text-[#94A3B8] bg-[#0C1626] px-2 py-0.5 rounded border border-[#243449]">
              ID: {investigation.accessionId}
            </span>
          ) : (
            <span className="text-[10px] font-mono text-[#94A3B8] italic">
              NASA PSI
            </span>
          )}
        </div>

        <h4 className="text-base font-semibold text-[#F4F7FB] group-hover:text-[#35C6E8] transition-colors mb-2 line-clamp-1">
          {investigation.title}
        </h4>

        <p className="text-xs text-[#94A3B8] leading-relaxed mb-4 line-clamp-3">
          {investigation.description}
        </p>

        {investigation.facility && (
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-[#64748B] mb-4">
            <Tag className="w-3 h-3" />
            <span>Facility: {investigation.facility}</span>
          </div>
        )}
      </div>

      <div className="pt-3 border-t border-[#243449]/70 flex items-center justify-between">
        {investigation.isIllustrative && (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-amber-400/90 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
            <Sparkles className="w-2.5 h-2.5" />
            Preview Reference
          </span>
        )}
        <button
          onClick={() => onViewDetails(investigation.id)}
          className="ml-auto inline-flex items-center gap-1.5 text-xs font-medium text-[#35C6E8] hover:text-[#F4F7FB] transition-colors"
        >
          <span>View Details</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/common/PageHeader';
import { EmptyState } from '../components/common/EmptyState';
import { FileText, ArrowLeft } from 'lucide-react';

export const InvestigationDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-2">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-1.5 text-xs font-mono text-[#94A3B8] hover:text-[#35C6E8] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Catalog</span>
        </button>
      </div>

      <PageHeader
        title={`Investigation: ${id?.toUpperCase() || 'DETAILS'}`}
        subtitle="Scientific objectives, flight test matrix, physical parameters, and dataset provenance."
        badge="Detail View"
      />

      <EmptyState
        icon={FileText}
        title="Investigation Record Preview"
        description={`Record '${id}' will be fully populated with actual NASA PSI documents, objectives, hypotheses, and downloadable measurement files during Phase 4.`}
        actionText="View Investigations Catalog"
        onAction={() => navigate('/investigations')}
      />
    </div>
  );
};

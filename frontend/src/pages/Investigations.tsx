import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { EmptyState } from '../components/common/EmptyState';
import { Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Investigations: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Investigation Explorer"
        subtitle="Search and filter NASA Physical Sciences Informatics (PSI) microgravity combustion experiments."
        badge="Phase 4 Pipeline"
      />

      <EmptyState
        icon={Search}
        title="NASA PSI Ingestion Pipeline in Progress"
        description="The live investigation catalog is currently being ingested from NASA PSI. In Phase 4, full metadata, test matrices, and raw dataset links for BASS, FLEX, Saffire, and SAME will be populated."
        actionText="Return to Overview"
        onAction={() => navigate('/overview')}
      />
    </div>
  );
};

import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { EmptyState } from '../components/common/EmptyState';
import { Scale } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Comparison: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Comparison Studio"
        subtitle="Scientifically validated comparative analysis of microgravity combustion measurements."
        badge="Phase 5 Scientific Engine"
      />

      <EmptyState
        icon={Scale}
        title="Scientific Analysis Engine Pending Integration"
        description="The scientific comparison engine is slated for Phase 5. It will support unit normalization, physical dimension validation, and cross-experiment parameter comparisons (e.g. flame spread rate vs ambient oxygen concentration)."
        actionText="Return to Overview"
        onAction={() => navigate('/overview')}
      />
    </div>
  );
};

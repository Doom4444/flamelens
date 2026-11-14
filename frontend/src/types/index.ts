export type ConnectionStatus = 'connected' | 'disconnected' | 'checking';

export interface BackendHealthResponse {
  status: string;
  application: string;
  version: string;
  environment: string;
  timestamp: string;
}

export type ResearchCategoryType = 'prevention' | 'detection' | 'suppression';

export interface CategoryInfo {
  id: ResearchCategoryType;
  title: string;
  subtitle: string;
  description: string;
  exampleInvestigations: string[];
  focusAreas: string[];
  accentColor: string;
}

export interface InvestigationPreview {
  id: string;
  accessionId?: string;
  title: string;
  category: ResearchCategoryType;
  description: string;
  facility?: string;
  isIllustrative?: boolean;
}

export interface DashboardMetric {
  id: string;
  label: string;
  value: string | number;
  statusLabel: string;
  description: string;
  isPending: boolean;
}

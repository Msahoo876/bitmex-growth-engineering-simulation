export interface Period {
  start: string;
  end: string;
}

export interface FunnelStep {
  key: string;
  label: string;
  event_name: string;
  users: number;
  conversion_rate_from_previous?: number | null;
  conversion_rate_from_start: number;
}

export interface FunnelAnalytics {
  funnel_name: string;
  period: Period;
  steps: FunnelStep[];
  total_entered: number;
  total_completed: number;
  completion_rate: number;
}

export interface DropoffStep {
  from_step: string;
  to_step: string;
  users_lost: number;
  dropoff_rate: number;
}

export interface DropoffAnalytics {
  funnel_name: string;
  period: Period;
  steps: DropoffStep[];
  largest_dropoff_step?: string | null;
}

export interface RetentionPeriod {
  day: number;
  retained_users: number;
  retention_rate: number;
}

export interface RetentionAnalytics {
  anchor_event: string;
  period: Period;
  cohort_size: number;
  periods: RetentionPeriod[];
}

export interface SourceMetric {
  source: string;
  touch_type: string;
  users: number;
}

export interface CampaignMetric {
  campaign_name: string;
  source: string;
  touch_type: string;
  users: number;
}

export interface SourceAttribution {
  period: Period;
  metrics: SourceMetric[];
  top_source?: string | null;
}

export interface CampaignAttribution {
  period: Period;
  metrics: CampaignMetric[];
}

export interface TopSource {
  period: Period;
  source?: string | null;
  users: number;
}

export interface DataHealth {
  period: Period;
  health_score: number;
  summary: Record<string, number>;
  breakdown: Record<string, number>;
}

export interface Duplicates {
  total_duplicate_groups: number;
  total_duplicate_events: number;
}

export interface SchemaErrors {
  total_errors: number;
}

export interface FunnelIntegrity {
  total_broken_paths: number;
}

export interface Anomalies {
  total_anomalies: number;
  daily_volume: Record<string, number>;
}

export interface InsightRecommendation {
  text: string;
  category: string;
  impact: string;
  effort: string;
}

export interface Insight {
  id: string;
  insight_type: string;
  title: string;
  summary: string;
  recommendations: InsightRecommendation[];
  input_metrics?: Record<string, unknown> | null;
  model_name?: string | null;
  priority?: string | null;
  created_at: string;
}

export interface InsightList {
  insights: Insight[];
}

export interface GeneratedInsights {
  insights: Insight[];
  generated_count: number;
}

export interface ExecutiveSummary {
  title: string;
  summary: string;
  recommendations: InsightRecommendation[];
  health_score?: number | null;
  top_source?: string | null;
  generated_at?: string | null;
}

export interface EventHealth {
  period_hours: number;
  total_ingested: number;
  valid_events: number;
  invalid_events: number;
  acceptance_rate: number;
  duplicate_events: number;
  events_by_name: Record<string, number>;
  validation_breakdown: { code: string; count: number }[];
  health_score: number;
}

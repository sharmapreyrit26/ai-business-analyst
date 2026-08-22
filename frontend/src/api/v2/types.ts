import type {
  AnalyticsContext,
} from '../../platform/analytics-context'

import type {
  MetricContract,
  MetricQuality,
} from '../../types/metric'


export type PlatformHealth = {
  status: string
  version: string
  architecture: string
}


export type PlatformCapabilities = {
  analytics_context: boolean
  global_filters: boolean
  metric_contracts: boolean
  metric_dictionary: boolean
  drilldowns: boolean
  scenario_v2: boolean
  investigations: boolean
  alerts: boolean
  exports: boolean
  saved_views: boolean
  workspaces: boolean
  brands: boolean
  data_sources: boolean
  data_quality: boolean

  scenario_controls: ScenarioControl[]
}


export type MetricDefinition = {
  metric_id: string
  label: string
  unit: string
  definition?: string | null
  formula?: string | null
  higher_is_better?: boolean | null
  source_engine?: string | null
  source_tables: string[]
  source_fields: string[]
  grain?: string | null
  data_quality: string
  limitations: string[]
}


export type MetricListResponse = {
  count: number
  data: MetricDefinition[]
}


export type MetricLineage = {
  metric_id: string
  label: string
  formula?: string | null
  source_engine?: string | null
  source_tables: string[]
  source_fields: string[]
  grain?: string | null
  limitations: string[]
}


export type DrilldownComponent = {
  component_id: string
  label: string
  value?: number | null
  formatted_value?: string | null
  operator?: string | null
  contribution_to_change?: number | null
  metadata: Record<
    string,
    unknown
  >
}


export type DrilldownSource = {
  source_type: string
  source_name: string
  fields: string[]
  description?: string | null
}


export type MetricDrilldown = {
  metric: MetricContract

  calculation_components:
    DrilldownComponent[]

  sources:
    DrilldownSource[]

  limitations:
    string[]

  data_quality:
    MetricQuality

  related_metrics:
    string[]

  suggested_questions:
    string[]

  metadata:
    Record<
      string,
      unknown
    >
}


export type ScenarioControl = {
  control_id: string
  label: string
  unit: string
  enabled: boolean
  combined_supported: boolean
  minimum?: number | null
  maximum?: number | null
  step?: number | null
  description?: string | null
  limitation?: string | null
}


export type ScenarioChanges = {
  orders_change_percent: number
  aov_change_percent: number
  rto_reduction_percent: number
  marketing_spend_change_percent: number
  cac_change_percent: number
  discount_rate_change_percent: number
}


export type ScenarioV2Request = {
  month: string
  name?: string | null
  changes: ScenarioChanges
}


export type ScenarioWaterfallItem = {
  driver_id: string
  label: string
  impact?: number | null
  formatted_impact?: string | null
  direction: string
}


export type ScenarioExplanation = {
  headline: string
  explanation: string
  evidence: string[]
}


export type ScenarioV2Response = {
  status: string
  month: string
  name?: string | null
  scenario_type: string

  changes:
    ScenarioChanges

  current:
    Record<
      string,
      unknown
    >

  projected:
    Record<
      string,
      unknown
    >

  difference:
    Record<
      string,
      unknown
    >

  waterfall:
    ScenarioWaterfallItem[]

  explanations:
    ScenarioExplanation[]

  assumptions:
    string[]

  limitations:
    string[]
}


export type Investigation = {
  investigation_id: string
  title: string
  category: string
  severity:
    | 'critical'
    | 'warning'
    | 'info'

  status:
    | 'open'
    | 'investigating'
    | 'resolved'
    | 'dismissed'

  confidence:
    | 'high'
    | 'medium'
    | 'low'

  month: string
  summary: string

  estimated_impact?:
    number | null

  formatted_impact?:
    string | null

  primary_metric_id?:
    string | null

  drivers: unknown[]
  evidence: unknown[]
  recommended_actions: unknown[]
  related_metrics: string[]
  related_pages: string[]
  scenario_suggestions: string[]

  metadata:
    Record<
      string,
      unknown
    >
}


export type InvestigationListResponse = {
  month: string
  count: number
  data: Investigation[]
}


export type AlertResult = {
  alert_rule_id: string
  name: string
  metric_id: string
  triggered: boolean
  severity:
    | 'critical'
    | 'warning'
    | 'info'

  status:
    | 'active'
    | 'triggered'
    | 'disabled'

  current_value?:
    number | null

  threshold: number
  operator: string
  message: string
  page?: string | null

  metadata:
    Record<
      string,
      unknown
    >
}


export type AlertListResponse = {
  month: string
  triggered_count: number
  total_rules: number
  data: AlertResult[]
}


export type ExportFormat =
  | 'csv'
  | 'json'
  | 'xlsx'
  | 'pdf'


export type ExportDelivery =
  | 'download'
  | 'email'


export type ExportRequest = {
  report_id: string
  month?: string | null

  analytics_context?:
    AnalyticsContext | null

  format:
    ExportFormat

  delivery:
    ExportDelivery

  email?: string | null
  filename?: string | null

  include_metadata?:
    boolean
}


export type ExportResponse = {
  export_id: string
  report_id: string
  status:
    | 'ready'
    | 'pending'
    | 'unsupported'

  format:
    ExportFormat

  delivery:
    ExportDelivery

  filename: string
  mime_type: string
  row_count: number

  content?:
    string | null

  email?:
    string | null

  metadata:
    Record<
      string,
      unknown
    >

  limitations:
    string[]
}

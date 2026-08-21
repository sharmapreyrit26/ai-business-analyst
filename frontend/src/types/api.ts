export type GrowthMetric = {
  value?: number | null
  previous_value?: number | null
  growth_percent?: number | null
}

export type ReportingPeriodsResponse = {
  months: string[]
  complete_months: string[]
  partial_months: string[]
  default_month: string | null
}

export type DashboardResponse = {
  month: string
  kpis: {
    month: string
    data_quality: { status?: string; is_partial_month?: boolean }
    revenue: GrowthMetric
    orders: GrowthMetric
    aov: GrowthMetric
    delivery: { rate_percent?: number | null; delivered_orders?: number | null }
    cancellation: { rate_percent?: number | null; cancelled_orders?: number | null }
    freight: { value?: number | null }
    items: { value?: number | null }
    business_totals?: Record<string, number>
  }
  monthly_revenue: Array<Record<string, number | string | null>>
  data_quality: Array<Record<string, unknown>>
  insights: Record<string, unknown>
}

export type ProductAnalyticsResponse = {
  month?: string | null
  summary: Record<string, any>
  top_products: Array<Record<string, any>>
  concentration: Record<string, any>
  available_metrics: string[]
  unavailable_metrics: Record<string, any>
}

export type CustomerAnalyticsResponse = {
  status: string
  data_quality: Record<string, any>
  available_analysis: Record<string, any>
  unavailable_analysis: Record<string, any>
  next_data_requirement: Record<string, any>
}

export type LogisticsAnalyticsResponse = {
  month?: string | null
  fulfilment_tat: Record<string, any>
  delivery_promise: Record<string, any>
  order_status: Record<string, any>
  data_quality: Record<string, any>
  available_metrics: string[]
  unavailable_metrics: Record<string, any>
}

export type BusinessAnswerResponse = {
  question: string
  month: string
  question_type: string
  analysis_execution?: {
    total_steps: number
    successful_steps: number
    failed_steps: number
  } | null
  ai_available: boolean
  answer: {
    answer: string
    evidence: string[]
    likely_driver: string
    recommended_actions: string[]
  }
}

export type ScenarioResponse = {
  question: string
  month: string
  status: string
  scenario_type?: string | null
  parameters?: Record<string, any> | null
  parser_result?: Record<string, any> | null
  scenario_result?: Record<string, any> | null
}

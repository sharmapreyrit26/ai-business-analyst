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

export type ProductRow = {
  product_id?: string
  revenue?: number
  units_sold?: number
  orders?: number
  average_selling_price?: number
  freight_value?: number
  revenue_share_percent?: number
  freight_to_revenue_percent?: number
}

export type ProductAnalyticsResponse = {
  month?: string | null
  summary: {
    status?: string
    total_products?: number
    total_revenue?: number
    total_units?: number
    total_orders?: number
    average_revenue_per_product?: number
    [key: string]: unknown
  }
  top_products: ProductRow[]
  concentration: {
    top_1_revenue_share_percent?: number
    top_5_revenue_share_percent?: number
    top_10_revenue_share_percent?: number
    [key: string]: unknown
  }
  available_metrics: string[]
  unavailable_metrics: Record<string, unknown>
}

export type CustomerAnalyticsResponse = {
  status: string
  data_quality: Record<string, unknown>
  available_analysis: Record<string, unknown>
  unavailable_analysis: Record<string, unknown>
  next_data_requirement: Record<string, unknown>
}

export type TatMetric = {
  unit?: string
  average?: number
  median?: number
  p90?: number
  sample_size?: number
}

export type LogisticsAnalyticsResponse = {
  month?: string | null
  fulfilment_tat: {
    purchase_to_approval?: TatMetric
    approval_to_carrier?: TatMetric
    carrier_to_delivery?: TatMetric
    purchase_to_delivery?: TatMetric
    [key: string]: unknown
  }
  delivery_promise: Record<string, unknown>
  order_status: Record<string, unknown>
  data_quality: Record<string, unknown>
  available_metrics: string[]
  unavailable_metrics: Record<string, unknown>
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
  parameters?: Record<string, unknown> | null
  parser_result?: Record<string, unknown> | null
  scenario_result?: Record<string, unknown> | null
}

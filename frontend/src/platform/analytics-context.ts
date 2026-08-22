export type ComparisonMode =
  | 'none'
  | 'previous_period'
  | 'previous_month'
  | 'previous_year'
  | 'custom'

export type AnalyticsFilters = {
  channels: string[]
  categories: string[]
  skus: string[]
  couriers: string[]
  warehouses: string[]
  payment_methods: string[]
  states: string[]
  zones: string[]
}

export type AnalyticsPeriod = {
  start_date: string
  end_date: string
}

export type ComparisonPeriod = {
  mode: ComparisonMode
  start_date?: string | null
  end_date?: string | null
}

export type AnalyticsContext = {
  workspace_id?: string | null
  brand_id?: string | null

  period: AnalyticsPeriod

  comparison: ComparisonPeriod

  filters: AnalyticsFilters
}

export const emptyFilters: AnalyticsFilters = {
  channels: [],
  categories: [],
  skus: [],
  couriers: [],
  warehouses: [],
  payment_methods: [],
  states: [],
  zones: [],
}

export const defaultAnalyticsContext: AnalyticsContext = {
  period: {
    start_date: '2025-11-01',
    end_date: '2025-11-30',
  },

  comparison: {
    mode: 'previous_month',
  },

  filters: {
    ...emptyFilters,
  },
}

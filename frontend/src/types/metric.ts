export type MetricUnit =
  | 'currency'
  | 'percent'
  | 'ratio'
  | 'count'
  | 'days'
  | 'decimal'

export type MetricDirection =
  | 'up'
  | 'down'
  | 'flat'
  | 'unknown'

export type MetricSentiment =
  | 'positive'
  | 'negative'
  | 'neutral'
  | 'warning'
  | 'unknown'

export type MetricQuality =
  | 'verified'
  | 'partial'
  | 'estimated'
  | 'unavailable'

export type MetricComparison = {
  previous_value?: number | null
  change_absolute?: number | null
  change_percent?: number | null
  direction: MetricDirection
}

export type MetricSource = {
  engine?: string | null
  tables: string[]
  fields: string[]
}

export type MetricContract = {
  metric_id: string
  label: string

  value?: number | null
  formatted_value?: string | null

  unit: MetricUnit

  comparison: MetricComparison

  sentiment: MetricSentiment

  definition?: string | null
  formula?: string | null

  data_quality: MetricQuality

  source: MetricSource

  metadata: Record<string, unknown>
}

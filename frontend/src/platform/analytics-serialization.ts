import type {
  AnalyticsContext,
  AnalyticsFilters,
} from './analytics-context'


export function
serializeAnalyticsContext(
  analytics: AnalyticsContext
): AnalyticsContext {
  return {
    workspace_id:
      analytics.workspace_id
      ?? null,

    brand_id:
      analytics.brand_id
      ?? null,

    period: {
      start_date:
        analytics.period.start_date,

      end_date:
        analytics.period.end_date,
    },

    comparison: {
      mode:
        analytics.comparison.mode,

      start_date:
        analytics.comparison
          .start_date
        ?? null,

      end_date:
        analytics.comparison
          .end_date
        ?? null,
    },

    filters:
      serializeFilters(
        analytics.filters
      ),
  }
}


export function
serializeFilters(
  filters: AnalyticsFilters
): AnalyticsFilters {
  return {
    channels:
      [...filters.channels],

    categories:
      [...filters.categories],

    skus:
      [...filters.skus],

    couriers:
      [...filters.couriers],

    warehouses:
      [...filters.warehouses],

    payment_methods:
      [
        ...filters
          .payment_methods,
      ],

    states:
      [...filters.states],

    zones:
      [...filters.zones],
  }
}


export function
activeFilterCount(
  filters: AnalyticsFilters
): number {
  return Object
    .values(
      filters
    )
    .reduce(
      (
        total,
        values,
      ) =>
        total
        + values.length,
      0
    )
}

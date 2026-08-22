import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  CircleDollarSign,
  Megaphone,
  PackageSearch,
  RefreshCcw,
  ShieldAlert,
  ShoppingCart,
  Truck,
  Users,
} from 'lucide-react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  api,
} from '../api/profitlens'

import {
  apiV2,
} from '../api/v2/profitlens-v2'

import type {
  AlertListResponse,
  InvestigationListResponse,
} from '../api/v2/types'

import {
  MetricCard,
} from '../components/metrics/MetricCard'

import {
  MetricDrilldownDrawer,
} from '../components/metrics/MetricDrilldownDrawer'

import {
  useMetricDrilldown,
} from '../components/metrics/useMetricDrilldown'

import type {
  MetricContract,
  MetricSentiment,
  MetricUnit,
} from '../types/metric'


type BusinessHealthProps = {
  month: string
}


type OverviewData = Record<
  string,
  any
>


function formatCurrency(
  value: number | null | undefined
) {
  if (
    value === null
    || value === undefined
    || Number.isNaN(value)
  ) {
    return '—'
  }

  return new Intl.NumberFormat(
    'en-IN',
    {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }
  ).format(
    value
  )
}


function metric(
  input: {
    metricId: string
    label: string
    value?: number | null
    formattedValue?: string | null
    unit: MetricUnit
    changePercent?: number | null
    higherIsBetter?: boolean | null
    definition?: string
  }
): MetricContract {
  const change =
    input.changePercent

  let direction:
    MetricContract[
      'comparison'
    ]['direction'] =
      'unknown'

  if (
    change !== null
    && change !== undefined
  ) {
    if (change > 0) {
      direction = 'up'
    } else if (change < 0) {
      direction = 'down'
    } else {
      direction = 'flat'
    }
  }


  let sentiment:
    MetricSentiment =
      'neutral'

  if (
    change !== null
    && change !== undefined
    && input.higherIsBetter
    !== null
    && input.higherIsBetter
    !== undefined
  ) {
    if (change === 0) {
      sentiment = 'neutral'
    } else if (
      input.higherIsBetter
    ) {
      sentiment =
        change > 0
          ? 'positive'
          : 'negative'
    } else {
      sentiment =
        change < 0
          ? 'positive'
          : 'negative'
    }
  }


  return {
    metric_id:
      input.metricId,

    label:
      input.label,

    value:
      input.value
      ?? null,

    formatted_value:
      input.formattedValue
      ?? null,

    unit:
      input.unit,

    comparison: {
      previous_value:
        null,

      change_absolute:
        null,

      change_percent:
        change
        ?? null,

      direction,
    },

    sentiment,

    definition:
      input.definition
      ?? null,

    formula:
      null,

    data_quality:
      'verified',

    source: {
      engine:
        null,

      tables:
        [],

      fields:
        [],
    },

    metadata:
      {},
  }
}


function severityRank(
  severity: string
) {
  if (
    severity
    === 'critical'
  ) {
    return 0
  }

  if (
    severity
    === 'warning'
  ) {
    return 1
  }

  return 2
}


export default function BusinessHealth({
  month,
}: BusinessHealthProps) {
  const navigate =
    useNavigate()

  const [
    overview,
    setOverview,
  ] = useState<
    OverviewData | null
  >(null)

  const [
    investigations,
    setInvestigations,
  ] = useState<
    InvestigationListResponse | null
  >(null)

  const [
    alerts,
    setAlerts,
  ] = useState<
    AlertListResponse | null
  >(null)

  const [
    loading,
    setLoading,
  ] = useState(
    true
  )

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null)

  const drilldown =
    useMetricDrilldown()


  useEffect(
    () => {
      let cancelled =
        false

      setLoading(true)
      setError(null)

      /*
       * Clear month-specific secondary intelligence
       * while new data is loading.
       */
      setInvestigations(
        null
      )

      setAlerts(
        null
      )


      /*
       * ------------------------------------------------
       * PRIMARY DATA
       * ------------------------------------------------
       *
       * Business Health should render as soon as
       * deterministic overview data is available.
       *
       * Alerts and investigations must never block
       * the founder's main dashboard.
       */

      api.overview(
        month
      )
        .then(
          overviewResponse => {
            if (
              cancelled
            ) {
              return
            }

            setOverview(
              overviewResponse as unknown as OverviewData
            )

            setLoading(
              false
            )
          }
        )
        .catch(
          requestError => {
            if (
              cancelled
            ) {
              return
            }

            setOverview(
              null
            )

            setError(
              requestError
                instanceof Error
                ? requestError.message
                : (
                    'Could not load '
                    + 'Business Health.'
                  )
            )

            setLoading(
              false
            )
          }
        )


      /*
       * ------------------------------------------------
       * SECONDARY INTELLIGENCE
       * ------------------------------------------------
       *
       * Run concurrently, but independently from the
       * critical overview render.
       *
       * One failed intelligence endpoint must not
       * crash or block Business Health.
       */

      void Promise.allSettled([
        apiV2.investigations(
          month
        ),

        apiV2.alerts(
          month
        ),
      ])
        .then(
          results => {
            if (
              cancelled
            ) {
              return
            }

            const [
              investigationResult,
              alertResult,
            ] = results


            if (
              investigationResult.status
              === 'fulfilled'
            ) {
              setInvestigations(
                investigationResult.value
              )
            }


            if (
              alertResult.status
              === 'fulfilled'
            ) {
              setAlerts(
                alertResult.value
              )
            }
          }
        )


      return () => {
        cancelled = true
      }
    },
    [
      month,
    ]
  )


  const metrics =
    useMemo(
      () => {
        if (
          !overview
        ) {
          return []
        }

        const revenue =
          overview.revenue
          ?? {}

        const profitability =
          overview.profitability
          ?? {}

        const marketing =
          overview.marketing
          ?? {}

        const customers =
          overview.customers
          ?? {}

        const logistics =
          overview.logistics
          ?? {}


        return [
          metric({
            metricId:
              'realized_revenue',

            label:
              'Realized Revenue',

            value:
              revenue
                .realized_revenue,

            formattedValue:
              formatCurrency(
                revenue
                  .realized_revenue
              ),

            unit:
              'currency',

            changePercent:
              revenue
                .revenue_growth_percent,

            higherIsBetter:
              true,

            definition:
              'Realized revenue for the selected reporting period.',
          }),

          metric({
            metricId:
              'contribution_profit_after_marketing',

            label:
              'Contribution Profit',

            value:
              profitability
                .contribution_profit_after_marketing,

            formattedValue:
              formatCurrency(
                profitability
                  .contribution_profit_after_marketing
              ),

            unit:
              'currency',

            changePercent:
              profitability
                .profit_after_marketing_growth_percent,

            higherIsBetter:
              true,
          }),

          metric({
            metricId:
              'contribution_margin_after_marketing_percent',

            label:
              'Contribution Margin',

            value:
              profitability
                .contribution_margin_after_marketing_percent,

            formattedValue:
              profitability
                .contribution_margin_after_marketing_percent
              !== undefined
                ? (
                    `${Number(
                      profitability
                        .contribution_margin_after_marketing_percent
                    ).toFixed(2)}%`
                  )
                : '—',

            unit:
              'percent',

            higherIsBetter:
              true,
          }),

          metric({
            metricId:
              'blended_roas',

            label:
              'Blended ROAS',

            value:
              marketing
                .blended_roas,

            formattedValue:
              marketing
                .blended_roas
              !== undefined
                ? (
                    `${Number(
                      marketing
                        .blended_roas
                    ).toFixed(2)}x`
                  )
                : '—',

            unit:
              'ratio',

            higherIsBetter:
              true,
          }),

          metric({
            metricId:
              'rto_rate_percent',

            label:
              'RTO Rate',

            value:
              logistics
                .rto_rate_percent,

            formattedValue:
              logistics
                .rto_rate_percent
              !== undefined
                ? (
                    `${Number(
                      logistics
                        .rto_rate_percent
                    ).toFixed(2)}%`
                  )
                : '—',

            unit:
              'percent',

            higherIsBetter:
              false,
          }),

          metric({
            metricId:
              'repeat_customer_rate_percent',

            label:
              'Repeat Customer Rate',

            value:
              customers
                .repeat_customer_rate_percent,

            formattedValue:
              customers
                .repeat_customer_rate_percent
              !== undefined
                ? (
                    `${Number(
                      customers
                        .repeat_customer_rate_percent
                    ).toFixed(2)}%`
                  )
                : '—',

            unit:
              'percent',

            higherIsBetter:
              true,
          }),
        ]
      },
      [
        overview,
      ]
    )


  const topInvestigations =
    useMemo(
      () => (
        investigations
          ?.data
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              severityRank(
                first.severity
              )
              - severityRank(
                  second.severity
                )
          )
          .slice(
            0,
            4
          )
        ?? []
      ),
      [
        investigations,
      ]
    )


  const triggeredAlerts =
    useMemo(
      () => (
        alerts
          ?.data
          .filter(
            item =>
              item.triggered
          )
          .slice(
            0,
            4
          )
        ?? []
      ),
      [
        alerts,
      ]
    )


  function openMetric(
    selected:
      MetricContract
  ) {
    if (
      selected.value
      === null
      || selected.value
      === undefined
    ) {
      return
    }

    void drilldown.openMetric({
      metricId:
        selected.metric_id,

      value:
        Number(
          selected.value
        ),
    })
  }


  if (
    loading
  ) {
    return (
      <div className="pl-business-health">
        <div className="pl-page-state">
          <RefreshCcw
            size={20}
          />

          Loading Business Health...
        </div>
      </div>
    )
  }


  if (
    error
    || !overview
  ) {
    return (
      <div className="pl-business-health">

        <div className="pl-page-state error">

          <AlertTriangle
            size={20}
          />

          <div>
            <strong>
              Could not load data
            </strong>

            <span>
              {
                error
                ?? (
                  'Could not load '
                  + 'Business Health.'
                )
              }
            </span>
          </div>

        </div>

      </div>
    )
  }


  const revenue =
    overview.revenue
    ?? {}

  const profitability =
    overview.profitability
    ?? {}

  const marketing =
    overview.marketing
    ?? {}

  const logistics =
    overview.logistics
    ?? {}

  const customers =
    overview.customers
    ?? {}


  return (
    <div className="pl-business-health">

      <section className="pl-business-hero">

        <div>

          <div className="pl-page-eyebrow">
            Founder command center
          </div>

          <h1>
            Business Health
          </h1>

          <p>
            What changed, what needs attention,
            and where to act next for {month}.
          </p>

        </div>


        <div className="pl-business-hero-actions">

          <button
            type="button"
            className="pl-secondary-button"
            onClick={() =>
              navigate(
                '/analyst'
              )
            }
          >
            Ask ProfitLens
          </button>

          <button
            type="button"
            className="pl-primary-button"
            onClick={() =>
              navigate(
                '/scenario'
              )
            }
          >
            Run scenario
          </button>

        </div>

      </section>


      <section className="pl-health-strip">

        <div className="pl-health-strip-item">

          <ShoppingCart
            size={18}
          />

          <div>
            <span>
              Orders
            </span>

            <strong>
              {
                Number(
                  revenue.orders
                  ?? 0
                )
                  .toLocaleString(
                    'en-IN'
                  )
              }
            </strong>
          </div>

        </div>


        <div className="pl-health-strip-item">

          <CircleDollarSign
            size={18}
          />

          <div>
            <span>
              AOV
            </span>

            <strong>
              {
                formatCurrency(
                  revenue.aov
                )
              }
            </strong>
          </div>

        </div>


        <div className="pl-health-strip-item">

          <Megaphone
            size={18}
          />

          <div>
            <span>
              Marketing Spend
            </span>

            <strong>
              {
                formatCurrency(
                  marketing
                    .marketing_spend
                  ?? profitability
                    .marketing_spend
                )
              }
            </strong>
          </div>

        </div>


        <div className="pl-health-strip-item">

          <Truck
            size={18}
          />

          <div>
            <span>
              Delivery Rate
            </span>

            <strong>
              {
                logistics
                  .delivery_rate_percent
                !== undefined
                  ? (
                      `${Number(
                        logistics
                          .delivery_rate_percent
                      ).toFixed(2)}%`
                    )
                  : '—'
              }
            </strong>
          </div>

        </div>


        <div className="pl-health-strip-item">

          <Users
            size={18}
          />

          <div>
            <span>
              Customers
            </span>

            <strong>
              {
                Number(
                  customers
                    .active_customers
                  ?? customers
                    .customers
                  ?? 0
                )
                  .toLocaleString(
                    'en-IN'
                  )
              }
            </strong>
          </div>

        </div>

      </section>


      <section>

        <div className="pl-section-header">

          <div>

            <h2>
              Core business metrics
            </h2>

            <p>
              Click any metric to inspect its
              calculation, source and data quality.
            </p>

          </div>

        </div>


        <div className="pl-metric-grid">

          {
            metrics.map(
              item => (
                <MetricCard
                  key={
                    item.metric_id
                  }
                  metric={
                    item
                  }
                  onClick={
                    openMetric
                  }
                />
              )
            )
          }

        </div>

      </section>


      <section className="pl-founder-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                ProfitLens detected
              </span>

              <h2>
                Investigations
              </h2>

            </div>

            <button
              type="button"
              className="pl-text-button"
              onClick={() =>
                navigate(
                  '/investigations'
                )
              }
            >
              View all

              <ArrowRight
                size={14}
              />
            </button>

          </div>


          {
            topInvestigations.length
            > 0
              ? (
                <div className="pl-investigation-list">

                  {
                    topInvestigations.map(
                      item => (
                        <button
                          key={
                            item.investigation_id
                          }
                          type="button"
                          className="pl-investigation-row"
                          onClick={() => {
                            const target =
                              item.related_pages?.[0]

                            if (
                              target
                            ) {
                              navigate(
                                target
                              )
                            }
                          }}
                        >

                          <div
                            className={
                              `pl-severity-icon ${
                                item.severity
                              }`
                            }
                          >
                            <ShieldAlert
                              size={16}
                            />
                          </div>

                          <div className="pl-investigation-copy">

                            <div>
                              <strong>
                                {
                                  item.title
                                }
                              </strong>

                              <span
                                className={
                                  `pl-severity-badge ${
                                    item.severity
                                  }`
                                }
                              >
                                {
                                  item.severity
                                }
                              </span>
                            </div>

                            <p>
                              {
                                item.summary
                              }
                            </p>

                            {
                              item.formatted_impact
                              && (
                                <small>
                                  Estimated impact:
                                  {' '}
                                  {
                                    item.formatted_impact
                                  }
                                </small>
                              )
                            }

                          </div>


                          <ArrowRight
                            size={15}
                          />

                        </button>
                      )
                    )
                  }

                </div>
              )
              : (
                <div className="pl-empty-panel">

                  <CheckCircle2
                    size={20}
                  />

                  No material investigations
                  detected for this period.

                </div>
              )
          }

        </div>


        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Threshold monitoring
              </span>

              <h2>
                Active alerts
              </h2>

            </div>


            <div className="pl-panel-count">
              {
                alerts
                  ?.triggered_count
                ?? 0
              }
            </div>

          </div>


          {
            triggeredAlerts.length
            > 0
              ? (
                <div className="pl-alert-list">

                  {
                    triggeredAlerts.map(
                      item => (
                        <button
                          key={
                            item.alert_rule_id
                          }
                          type="button"
                          className="pl-alert-row"
                          onClick={() => {
                            if (
                              item.page
                            ) {
                              navigate(
                                item.page
                              )
                            }
                          }}
                        >

                          <div
                            className={
                              `pl-alert-indicator ${
                                item.severity
                              }`
                            }
                          />

                          <div>

                            <strong>
                              {
                                item.name
                              }
                            </strong>

                            <span>
                              {
                                item.message
                              }
                            </span>

                          </div>


                          <ArrowRight
                            size={14}
                          />

                        </button>
                      )
                    )
                  }

                </div>
              )
              : (
                <div className="pl-empty-panel">

                  <CheckCircle2
                    size={20}
                  />

                  All configured metrics are
                  within thresholds.

                </div>
              )
          }

        </div>

      </section>


      <section className="pl-quick-actions">

        <button
          type="button"
          onClick={() =>
            navigate(
              '/marketing'
            )
          }
        >
          <Megaphone
            size={18}
          />

          <div>
            <strong>
              Review marketing
            </strong>

            <span>
              ROAS, CAC and channel efficiency
            </span>
          </div>

          <ArrowRight
            size={15}
          />
        </button>


        <button
          type="button"
          onClick={() =>
            navigate(
              '/products'
            )
          }
        >
          <PackageSearch
            size={18}
          />

          <div>
            <strong>
              Review products
            </strong>

            <span>
              Revenue mix and product performance
            </span>
          </div>

          <ArrowRight
            size={15}
          />
        </button>


        <button
          type="button"
          onClick={() =>
            navigate(
              '/logistics'
            )
          }
        >
          <Truck
            size={18}
          />

          <div>
            <strong>
              Review logistics
            </strong>

            <span>
              RTO, NDR, delivery and courier risk
            </span>
          </div>

          <ArrowRight
            size={15}
          />
        </button>

      </section>


      <MetricDrilldownDrawer
        open={
          drilldown.open
        }

        loading={
          drilldown.loading
        }

        error={
          drilldown.error
        }

        data={
          drilldown.data
        }

        onClose={
          drilldown.closeMetric
        }

        onRelatedMetric={() => {
          /* related-metric chaining comes later */
        }}

        onSuggestedQuestion={
          () =>
            navigate(
              '/analyst'
            )
        }
      />

    </div>
  )
}

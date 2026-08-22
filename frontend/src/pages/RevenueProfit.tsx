import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowRight,
  BadgeIndianRupee,
  CircleDollarSign,
  Megaphone,
  RefreshCcw,
  ShoppingCart,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from 'lucide-react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  api,
} from '../api/profitlens'

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


type RevenueProfitProps = {
  month: string
}


type OverviewData = Record<
  string,
  any
>


type TrendPoint = {
  month: string
  revenue: number
  profit: number
  margin: number
}


function formatCurrency(
  value:
    number
    | null
    | undefined
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


function formatCompactCurrency(
  value: number
) {
  return new Intl.NumberFormat(
    'en-IN',
    {
      style: 'currency',
      currency: 'INR',
      notation: 'compact',
      maximumFractionDigits: 1,
    }
  ).format(
    value
  )
}


function previousMonths(
  month: string,
  count: number
) {
  const [
    year,
    monthNumber,
  ] = month
    .split('-')
    .map(Number)

  const result: string[] = []

  for (
    let index = count - 1;
    index >= 0;
    index -= 1
  ) {
    const date =
      new Date(
        year,
        monthNumber - 1 - index,
        1
      )

    result.push(
      `${date.getFullYear()}-${String(
        date.getMonth() + 1
      ).padStart(
        2,
        '0'
      )}`
    )
  }

  return result
}


function buildMetric(
  input: {
    metricId: string
    label: string

    value?:
      number
      | null

    formattedValue?:
      string
      | null

    unit:
      MetricUnit

    changePercent?:
      number
      | null

    higherIsBetter:
      boolean

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
  ) {
    if (change === 0) {
      sentiment =
        'neutral'
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


export default function RevenueProfit({
  month,
}: RevenueProfitProps) {
  const navigate =
    useNavigate()

  const drilldown =
    useMetricDrilldown()

  const [
    overview,
    setOverview,
  ] = useState<
    OverviewData | null
  >(null)

  const [
    trend,
    setTrend,
  ] = useState<
    TrendPoint[]
  >([])

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


  useEffect(
    () => {
      let cancelled =
        false

      setLoading(true)
      setError(null)
      setTrend([])

      /*
       * Critical render:
       * load the selected reporting month first.
       *
       * Historical trend requests must never
       * block the financial dashboard itself.
       */
      api.overview(
        month
      )
        .then(
          currentResponse => {
            if (
              cancelled
            ) {
              return
            }

            const current =
              currentResponse as unknown as OverviewData

            setOverview(
              current
            )

            setLoading(
              false
            )


            /*
             * Progressive enhancement:
             * historical trend loads only after
             * the current financial view exists.
             */
            const months =
              previousMonths(
                month,
                6
              )

            void Promise.allSettled(
              months.map(
                reportingMonth =>
                  api.overview(
                    reportingMonth
                  )
              )
            ).then(
              trendResponses => {
                if (
                  cancelled
                ) {
                  return
                }

                const trendRows:
                  TrendPoint[] = []

                trendResponses.forEach(
                  (
                    result,
                    index,
                  ) => {
                    if (
                      result.status
                      !== 'fulfilled'
                    ) {
                      return
                    }

                    const data =
                      result.value as unknown as OverviewData

                    trendRows.push({
                      month:
                        months[index],

                      revenue:
                        Number(
                          data
                            .revenue
                            ?.realized_revenue
                          ?? 0
                        ),

                      profit:
                        Number(
                          data
                            .profitability
                            ?.contribution_profit_after_marketing
                          ?? 0
                        ),

                      margin:
                        Number(
                          data
                            .profitability
                            ?.contribution_margin_after_marketing_percent
                          ?? 0
                        ),
                    })
                  }
                )

                setTrend(
                  trendRows
                )
              }
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
                    + 'Revenue & Profit.'
                  )
            )

            setLoading(
              false
            )
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


        return [
          buildMetric({
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
              'Revenue realized for the selected reporting period.',
          }),

          buildMetric({
            metricId:
              'gross_profit',

            label:
              'Gross Profit',

            value:
              profitability
                .gross_profit,

            formattedValue:
              formatCurrency(
                profitability
                  .gross_profit
              ),

            unit:
              'currency',

            higherIsBetter:
              true,
          }),

          buildMetric({
            metricId:
              'gross_margin_percent',

            label:
              'Gross Margin',

            value:
              profitability
                .gross_margin_percent,

            formattedValue:
              profitability
                .gross_margin_percent
              !== undefined
                ? (
                    `${Number(
                      profitability
                        .gross_margin_percent
                    ).toFixed(2)}%`
                  )
                : '—',

            unit:
              'percent',

            higherIsBetter:
              true,
          }),

          buildMetric({
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

          buildMetric({
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

          buildMetric({
            metricId:
              'aov',

            label:
              'Average Order Value',

            value:
              revenue.aov,

            formattedValue:
              formatCurrency(
                revenue.aov
              ),

            unit:
              'currency',

            higherIsBetter:
              true,
          }),
        ]
      },
      [
        overview,
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
      <div className="pl-revenue-profit">

        <div className="pl-page-state">
          <RefreshCcw
            size={20}
          />

          Loading Revenue & Profit...
        </div>

      </div>
    )
  }


  if (
    error
    || !overview
  ) {
    return (
      <div className="pl-revenue-profit">

        <div className="pl-page-state error">

          <AlertTriangle
            size={20}
          />

          <div>
            <strong>
              Could not load Revenue & Profit
            </strong>

            <span>
              {
                error
                ?? 'Financial data is unavailable.'
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


  const maxTrendRevenue =
    Math.max(
      1,
      ...trend.map(
        item =>
          item.revenue
      )
    )


  const bridge = [
    {
      label:
        'Gross profit',

      value:
        Number(
          profitability
            .gross_profit
          ?? 0
        ),

      type:
        'positive',
    },

    {
      label:
        'Operating / fulfillment impact',

      value:
        Number(
          profitability
            .contribution_profit_before_marketing
          ?? 0
        )
        - Number(
            profitability
              .gross_profit
            ?? 0
          ),

      type:
        'negative',
    },

    {
      label:
        'Marketing spend',

      value:
        -Number(
          profitability
            .marketing_spend
          ?? 0
        ),

      type:
        'negative',
    },

    {
      label:
        'Contribution profit',

      value:
        Number(
          profitability
            .contribution_profit_after_marketing
          ?? 0
        ),

      type:
        'total',
    },
  ]


  return (
    <div className="pl-revenue-profit">

      <section className="pl-business-hero">

        <div>

          <div className="pl-page-eyebrow">
            Financial performance
          </div>

          <h1>
            Revenue & Profit
          </h1>

          <p>
            Understand where revenue is changing,
            what is affecting margin and how much
            profit remains after marketing for {month}.
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
            <Sparkles
              size={14}
            />

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
            Test scenario

            <ArrowRight
              size={14}
            />
          </button>

        </div>

      </section>


      <section className="pl-financial-strip">

        <div>

          <ShoppingCart
            size={17}
          />

          <span>
            Orders
          </span>

          <strong>
            {
              Number(
                revenue.orders
                ?? 0
              ).toLocaleString(
                'en-IN'
              )
            }
          </strong>

          {
            revenue
              .order_growth_percent
            !== undefined
            && (
              <small
                className={
                  Number(
                    revenue
                      .order_growth_percent
                  ) >= 0
                    ? 'positive'
                    : 'negative'
                }
              >
                {
                  Number(
                    revenue
                      .order_growth_percent
                  ) >= 0
                    ? (
                        <TrendingUp
                          size={12}
                        />
                      )
                    : (
                        <TrendingDown
                          size={12}
                        />
                      )
                }

                {
                  Number(
                    revenue
                      .order_growth_percent
                  ).toFixed(
                    2
                  )
                }%
              </small>
            )
          }

        </div>


        <div>

          <BadgeIndianRupee
            size={17}
          />

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


        <div>

          <Megaphone
            size={17}
          />

          <span>
            Marketing Spend
          </span>

          <strong>
            {
              formatCurrency(
                profitability
                  .marketing_spend
              )
            }
          </strong>

        </div>


        <div>

          <CircleDollarSign
            size={17}
          />

          <span>
            Profit Before Marketing
          </span>

          <strong>
            {
              formatCurrency(
                profitability
                  .contribution_profit_before_marketing
              )
            }
          </strong>

        </div>

      </section>


      <section>

        <div className="pl-section-header">

          <div>

            <h2>
              Financial KPIs
            </h2>

            <p>
              Click a metric to inspect definition,
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


      <section className="pl-financial-analysis-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Six-month view
              </span>

              <h2>
                Revenue trend
              </h2>

            </div>

          </div>


          {
            trend.length > 0
              ? (
                <div className="pl-financial-trend">

                  {
                    trend.map(
                      item => {
                        const height =
                          Math.max(
                            6,
                            (
                              item.revenue
                              / maxTrendRevenue
                            )
                            * 100
                          )

                        return (
                          <div
                            key={
                              item.month
                            }
                            className="pl-financial-trend-column"
                          >

                            <div className="pl-financial-trend-value">
                              {
                                formatCompactCurrency(
                                  item.revenue
                                )
                              }
                            </div>

                            <div className="pl-financial-trend-track">

                              <div
                                className="pl-financial-trend-bar"
                                style={{
                                  height:
                                    `${height}%`,
                                }}
                              />

                            </div>

                            <strong>
                              {
                                item
                                  .month
                                  .slice(
                                    5
                                  )
                              }
                            </strong>

                            <span>
                              {
                                item.margin
                                  .toFixed(
                                    1
                                  )
                              }% margin
                            </span>

                          </div>
                        )
                      }
                    )
                  }

                </div>
              )
              : (
                <div className="pl-empty-panel">
                  Historical trend unavailable.
                </div>
              )
          }

        </div>


        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Profitability bridge
              </span>

              <h2>
                Where profit goes
              </h2>

            </div>

          </div>


          <div className="pl-profit-bridge">

            {
              bridge.map(
                (
                  item,
                  index,
                ) => (
                  <div
                    key={
                      item.label
                    }
                    className={
                      `pl-profit-bridge-row ${item.type}`
                    }
                  >

                    <div className="pl-profit-bridge-step">
                      {
                        index + 1
                      }
                    </div>

                    <div>

                      <span>
                        {
                          item.label
                        }
                      </span>

                      <strong>
                        {
                          item.value > 0
                            && item.type
                            !== 'total'
                              ? '+'
                              : ''
                        }

                        {
                          formatCurrency(
                            item.value
                          )
                        }
                      </strong>

                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>

      </section>


      <section className="pl-margin-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Margin progression
              </span>

              <h2>
                Margin stack
              </h2>

            </div>

          </div>


          <div className="pl-margin-stack">

            <div>

              <span>
                Gross margin
              </span>

              <strong>
                {
                  Number(
                    profitability
                      .gross_margin_percent
                    ?? 0
                  ).toFixed(
                    2
                  )
                }%
              </strong>

              <div>
                <i
                  style={{
                    width:
                      `${Math.max(
                        0,
                        Math.min(
                          100,
                          Number(
                            profitability
                              .gross_margin_percent
                            ?? 0
                          )
                        )
                      )}%`,
                  }}
                />
              </div>

            </div>


            <div>

              <span>
                Contribution margin
                before marketing
              </span>

              <strong>
                {
                  Number(
                    profitability
                      .contribution_margin_before_marketing_percent
                    ?? 0
                  ).toFixed(
                    2
                  )
                }%
              </strong>

              <div>
                <i
                  style={{
                    width:
                      `${Math.max(
                        0,
                        Math.min(
                          100,
                          Number(
                            profitability
                              .contribution_margin_before_marketing_percent
                            ?? 0
                          )
                        )
                      )}%`,
                  }}
                />
              </div>

            </div>


            <div>

              <span>
                Contribution margin
                after marketing
              </span>

              <strong>
                {
                  Number(
                    profitability
                      .contribution_margin_after_marketing_percent
                    ?? 0
                  ).toFixed(
                    2
                  )
                }%
              </strong>

              <div>
                <i
                  style={{
                    width:
                      `${Math.max(
                        0,
                        Math.min(
                          100,
                          Number(
                            profitability
                              .contribution_margin_after_marketing_percent
                            ?? 0
                          )
                        )
                      )}%`,
                  }}
                />
              </div>

            </div>

          </div>

        </div>


        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Decision shortcuts
              </span>

              <h2>
                Investigate further
              </h2>

            </div>

          </div>


          <div className="pl-financial-actions">

            <button
              type="button"
              onClick={() =>
                navigate(
                  '/marketing'
                )
              }
            >
              <Megaphone
                size={17}
              />

              <div>
                <strong>
                  Marketing efficiency
                </strong>

                <span>
                  Understand CAC, ROAS and spend impact.
                </span>
              </div>

              <ArrowRight
                size={14}
              />
            </button>


            <button
              type="button"
              onClick={() =>
                navigate(
                  '/investigations'
                )
              }
            >
              <TrendingDown
                size={17}
              />

              <div>
                <strong>
                  Revenue decline
                </strong>

                <span>
                  Investigate the drivers behind material changes.
                </span>
              </div>

              <ArrowRight
                size={14}
              />
            </button>


            <button
              type="button"
              onClick={() =>
                navigate(
                  '/scenario'
                )
              }
            >
              <Sparkles
                size={17}
              />

              <div>
                <strong>
                  Model recovery
                </strong>

                <span>
                  Test orders, AOV, RTO and marketing changes.
                </span>
              </div>

              <ArrowRight
                size={14}
              />
            </button>

          </div>

        </div>

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

        onSuggestedQuestion={() =>
          navigate(
            '/analyst'
          )
        }
      />

    </div>
  )
}

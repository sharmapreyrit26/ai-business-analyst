import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Megaphone,
  MousePointerClick,
  RefreshCcw,
  Sparkles,
  Target,
  TrendingDown,
  TrendingUp,
  Users,
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
  D2CMarketingCampaignRow,
  D2CMarketingChannelRow,
  D2CMarketingInsightsResponse,
  D2CMarketingSummaryResponse,
  D2CMarketingTrendRow,
} from '../types/api'

import type {
  MetricContract,
  MetricSentiment,
  MetricUnit,
} from '../types/metric'


type MarketingProps = {
  month: string
}


function formatCurrency(
  value: number
) {
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


function formatNumber(
  value: number
) {
  return new Intl.NumberFormat(
    'en-IN'
  ).format(
    value
  )
}


function buildMetric(
  input: {
    metricId: string
    label: string
    value: number
    formattedValue: string
    unit: MetricUnit

    changePercent?:
      number | null

    higherIsBetter:
      boolean

    definition?: string
  }
): MetricContract {
  const change =
    input.changePercent
    ?? null

  let direction:
    MetricContract[
      'comparison'
    ]['direction'] =
      'unknown'

  if (
    change !== null
  ) {
    if (
      change > 0
    ) {
      direction = 'up'
    } else if (
      change < 0
    ) {
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
    && change !== 0
  ) {
    if (
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
      input.value,

    formatted_value:
      input.formattedValue,

    unit:
      input.unit,

    comparison: {
      previous_value:
        null,

      change_absolute:
        null,

      change_percent:
        change,

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


export default function Marketing({
  month,
}: MarketingProps) {
  const navigate =
    useNavigate()

  const drilldown =
    useMetricDrilldown()

  const [
    summary,
    setSummary,
  ] = useState<
    D2CMarketingSummaryResponse | null
  >(
    null
  )

  const [
    channels,
    setChannels,
  ] = useState<
    D2CMarketingChannelRow[]
  >(
    []
  )

  const [
    campaigns,
    setCampaigns,
  ] = useState<
    D2CMarketingCampaignRow[]
  >(
    []
  )

  const [
    trend,
    setTrend,
  ] = useState<
    D2CMarketingTrendRow[]
  >(
    []
  )

  const [
    insights,
    setInsights,
  ] = useState<
    D2CMarketingInsightsResponse | null
  >(
    null
  )

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
  >(
    null
  )


  useEffect(
    () => {
      let cancelled =
        false

      setLoading(true)
      setError(null)

      Promise.all([
        api.marketing(
          month
        ),

        api.marketingChannels(
          month
        ),

        api.marketingCampaigns(
          month
        ),

        api.marketingTrend(),

        api.marketingInsights(
          month
        ),
      ])
        .then(
          ([
            summaryResponse,
            channelResponse,
            campaignResponse,
            trendResponse,
            insightsResponse,
          ]) => {
            if (
              cancelled
            ) {
              return
            }

            setSummary(
              summaryResponse
            )

            setChannels(
              channelResponse.data
            )

            setCampaigns(
              campaignResponse.data
            )

            setTrend(
              trendResponse.data
            )

            setInsights(
              insightsResponse
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

            setSummary(null)
            setChannels([])
            setCampaigns([])
            setTrend([])
            setInsights(null)

            setError(
              requestError
                instanceof Error
                ? requestError.message
                : (
                    'Could not load '
                    + 'marketing analytics.'
                  )
            )
          }
        )
        .finally(
          () => {
            if (
              !cancelled
            ) {
              setLoading(
                false
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


  const currentTrend =
    useMemo(
      () =>
        trend.find(
          row =>
            row.month
            === month
        )
        ?? null,
      [
        trend,
        month,
      ]
    )


  const metrics =
    useMemo(
      () => {
        if (
          !summary
        ) {
          return []
        }

        return [
          buildMetric({
            metricId:
              'marketing_spend',

            label:
              'Marketing Spend',

            value:
              summary
                .marketing_spend,

            formattedValue:
              formatCurrency(
                summary
                  .marketing_spend
              ),

            unit:
              'currency',

            changePercent:
              currentTrend
                ?.spend_growth_percent
              ?? null,

            higherIsBetter:
              false,

            definition:
              'Total marketing spend for the selected reporting period.',
          }),

          buildMetric({
            metricId:
              'attributed_revenue',

            label:
              'Attributed Revenue',

            value:
              summary
                .attributed_revenue,

            formattedValue:
              formatCurrency(
                summary
                  .attributed_revenue
              ),

            unit:
              'currency',

            changePercent:
              currentTrend
                ?.revenue_growth_percent
              ?? null,

            higherIsBetter:
              true,
          }),

          buildMetric({
            metricId:
              'blended_roas',

            label:
              'Blended ROAS',

            value:
              summary
                .blended_roas,

            formattedValue:
              `${summary
                .blended_roas
                .toFixed(2)}x`,

            unit:
              'ratio',

            changePercent:
              currentTrend
                ?.roas_change_percent
              ?? null,

            higherIsBetter:
              true,
          }),

          buildMetric({
            metricId:
              'cac',

            label:
              'Customer Acquisition Cost',

            value:
              summary.cac,

            formattedValue:
              formatCurrency(
                summary.cac
              ),

            unit:
              'currency',

            changePercent:
              currentTrend
                ?.cac_change_percent
              ?? null,

            higherIsBetter:
              false,
          }),

          buildMetric({
            metricId:
              'cost_per_order',

            label:
              'Cost Per Order',

            value:
              summary
                .cost_per_order,

            formattedValue:
              formatCurrency(
                summary
                  .cost_per_order
              ),

            unit:
              'currency',

            higherIsBetter:
              false,
          }),

          buildMetric({
            metricId:
              'session_conversion_percent',

            label:
              'Session Conversion',

            value:
              summary
                .session_conversion_percent,

            formattedValue:
              `${summary
                .session_conversion_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              true,
          }),
        ]
      },
      [
        summary,
        currentTrend,
      ]
    )


  const paidChannels =
    useMemo(
      () =>
        channels
          .filter(
            row =>
              row.spend > 0
          )
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second.roas
              - first.roas
          ),
      [
        channels,
      ]
    )


  const topCampaigns =
    useMemo(
      () =>
        campaigns
          .filter(
            row =>
              row.spend > 0
          )
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second.roas
              - first.roas
          )
          .slice(
            0,
            6
          ),
      [
        campaigns,
      ]
    )


  const weakestCampaigns =
    useMemo(
      () =>
        campaigns
          .filter(
            row =>
              row.spend > 0
          )
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              first.roas
              - second.roas
          )
          .slice(
            0,
            4
          ),
      [
        campaigns,
      ]
    )


  const visibleTrend =
    useMemo(
      () =>
        trend
          .filter(
            row =>
              row.month <= month
          )
          .slice(
            -6
          ),
      [
        trend,
        month,
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
      <div className="pl-marketing-v2">

        <div className="pl-page-state">

          <RefreshCcw
            size={20}
          />

          Loading marketing analytics...

        </div>

      </div>
    )
  }


  if (
    error
    || !summary
  ) {
    return (
      <div className="pl-marketing-v2">

        <div className="pl-page-state error">

          <AlertTriangle
            size={20}
          />

          <div>
            <strong>
              Could not load marketing
            </strong>

            <span>
              {
                error
                ?? 'Marketing data is unavailable.'
              }
            </span>
          </div>

        </div>

      </div>
    )
  }


  return (
    <div className="pl-marketing-v2">

      <section className="pl-business-hero">

        <div>

          <div className="pl-page-eyebrow">
            Growth efficiency
          </div>

          <h1>
            Marketing Performance
          </h1>

          <p>
            Understand spend efficiency,
            acquisition economics and campaign
            performance for {month}.
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
            Test spend scenario

            <ArrowRight
              size={14}
            />
          </button>

        </div>

      </section>


      <section className="pl-marketing-strip">

        <div>
          <Megaphone
            size={17}
          />

          <span>
            Paid ROAS
          </span>

          <strong>
            {
              summary
                .paid_roas
                .toFixed(2)
            }x
          </strong>
        </div>


        <div>
          <Users
            size={17}
          />

          <span>
            New Customers
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .new_customers
              )
            }
          </strong>
        </div>


        <div>
          <Target
            size={17}
          />

          <span>
            Attributed Orders
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .attributed_orders
              )
            }
          </strong>
        </div>


        <div>
          <MousePointerClick
            size={17}
          />

          <span>
            CTR
          </span>

          <strong>
            {
              summary
                .click_through_percent
                .toFixed(2)
            }%
          </strong>
        </div>

      </section>


      <section>

        <div className="pl-section-header">

          <div>

            <h2>
              Marketing health
            </h2>

            <p>
              Core acquisition economics for the
              selected reporting period.
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


      <section className="pl-marketing-insights-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Deterministic signal
              </span>

              <h2>
                Best ROAS channel
              </h2>

            </div>

            <TrendingUp
              size={18}
            />

          </div>


          <div className="pl-marketing-signal-value">
            {
              insights
                ?.best_roas_channel
                ?.channel
              ?? '—'
            }
          </div>

          <p>
            {
              insights
                ?.best_roas_channel
              ? (
                  `${insights
                    .best_roas_channel
                    .roas
                    .toFixed(2)}x ROAS`
                )
              : 'No paid channel available.'
            }
          </p>

        </div>


        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Acquisition efficiency
              </span>

              <h2>
                Lowest CAC channel
              </h2>

            </div>

            <Users
              size={18}
            />

          </div>


          <div className="pl-marketing-signal-value">
            {
              insights
                ?.lowest_cac_channel
                ?.channel
              ?? '—'
            }
          </div>

          <p>
            {
              insights
                ?.lowest_cac_channel
              ? (
                  `${formatCurrency(
                    insights
                      .lowest_cac_channel
                      .cac
                  )} CAC`
                )
              : 'Not available.'
            }
          </p>

        </div>


        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Revenue contribution
              </span>

              <h2>
                Highest revenue channel
              </h2>

            </div>

            <BarChart3
              size={18}
            />

          </div>


          <div className="pl-marketing-signal-value">
            {
              insights
                ?.highest_revenue_channel
                ?.channel
              ?? '—'
            }
          </div>

          <p>
            {
              insights
                ?.highest_revenue_channel
              ? formatCurrency(
                  insights
                    .highest_revenue_channel
                    .attributed_revenue
                )
              : 'Not available.'
            }
          </p>

        </div>

      </section>


      <section className="pl-marketing-analysis-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Allocation efficiency
              </span>

              <h2>
                Paid channel performance
              </h2>

            </div>

          </div>


          <div className="pl-channel-performance-list">

            {
              paidChannels.map(
                row => (
                  <div
                    key={
                      row.channel
                    }
                    className="pl-channel-performance-row"
                  >

                    <div>

                      <strong>
                        {
                          row.channel
                        }
                      </strong>

                      <span>
                        {
                          formatCurrency(
                            row.spend
                          )
                        }
                        {' spend'}
                      </span>

                    </div>


                    <div>

                      <strong>
                        {
                          row
                            .roas
                            .toFixed(2)
                        }x
                      </strong>

                      <span>
                        ROAS
                      </span>

                    </div>


                    <div>

                      <strong>
                        {
                          formatCurrency(
                            row.cac
                          )
                        }
                      </strong>

                      <span>
                        CAC
                      </span>

                    </div>


                    <div>

                      <strong>
                        {
                          formatCurrency(
                            row
                              .attributed_revenue
                          )
                        }
                      </strong>

                      <span>
                        Revenue
                      </span>

                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>


        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Six-month efficiency
              </span>

              <h2>
                ROAS vs CAC trend
              </h2>

            </div>

          </div>


          <div className="pl-marketing-trend-list">

            {
              visibleTrend.map(
                row => (
                  <div
                    key={
                      row.month
                    }
                    className="pl-marketing-trend-row"
                  >

                    <strong>
                      {
                        row.month
                      }
                    </strong>


                    <div>
                      <span>
                        ROAS
                      </span>

                      <strong>
                        {
                          row
                            .roas
                            .toFixed(2)
                        }x
                      </strong>
                    </div>


                    <div>
                      <span>
                        CAC
                      </span>

                      <strong>
                        {
                          formatCurrency(
                            row.cac
                          )
                        }
                      </strong>
                    </div>


                    <div
                      className={
                        row
                          .roas_change_percent
                        >= 0
                          ? 'positive'
                          : 'negative'
                      }
                    >
                      {
                        row
                          .roas_change_percent
                        >= 0
                          ? (
                              <TrendingUp
                                size={13}
                              />
                            )
                          : (
                              <TrendingDown
                                size={13}
                              />
                            )
                      }

                      {
                        row
                          .roas_change_percent
                          .toFixed(1)
                      }%
                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>

      </section>


      <section className="pl-marketing-campaign-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Scale candidates
              </span>

              <h2>
                Highest ROAS campaigns
              </h2>

            </div>

          </div>


          <div className="pl-campaign-list">

            {
              topCampaigns.map(
                row => (
                  <div
                    key={
                      `${row.channel}-${row.campaign}`
                    }
                    className="pl-campaign-row"
                  >

                    <div>

                      <strong>
                        {
                          row.campaign
                        }
                      </strong>

                      <span>
                        {
                          row.channel
                        }
                      </span>

                    </div>


                    <div>

                      <strong>
                        {
                          row
                            .roas
                            .toFixed(2)
                        }x
                      </strong>

                      <span>
                        ROAS
                      </span>

                    </div>


                    <div>

                      <strong>
                        {
                          formatCurrency(
                            row.cac
                          )
                        }
                      </strong>

                      <span>
                        CAC
                      </span>

                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>


        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Efficiency risk
              </span>

              <h2>
                Campaigns to review
              </h2>

            </div>

          </div>


          <div className="pl-campaign-list">

            {
              weakestCampaigns.map(
                row => (
                  <div
                    key={
                      `${row.channel}-${row.campaign}`
                    }
                    className="pl-campaign-row risk"
                  >

                    <div>

                      <strong>
                        {
                          row.campaign
                        }
                      </strong>

                      <span>
                        {
                          row.channel
                        }
                      </span>

                    </div>


                    <div>

                      <strong>
                        {
                          row
                            .roas
                            .toFixed(2)
                        }x
                      </strong>

                      <span>
                        ROAS
                      </span>

                    </div>


                    <div>

                      <strong>
                        {
                          formatCurrency(
                            row.cac
                          )
                        }
                      </strong>

                      <span>
                        CAC
                      </span>

                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>

      </section>


      <section className="pl-founder-panel">

        <div className="pl-panel-header">

          <div>

            <span className="pl-page-eyebrow">
              Detailed channel economics
            </span>

            <h2>
              Channel comparison
            </h2>

          </div>

        </div>


        <div className="table-wrap">

          <table className="data-table">

            <thead>
              <tr>
                <th>
                  Channel
                </th>

                <th>
                  Spend
                </th>

                <th>
                  Revenue
                </th>

                <th>
                  ROAS
                </th>

                <th>
                  CAC
                </th>

                <th>
                  Orders
                </th>

                <th>
                  Conversion
                </th>
              </tr>
            </thead>

            <tbody>

              {
                channels.map(
                  row => (
                    <tr
                      key={
                        row.channel
                      }
                    >

                      <td>
                        <strong>
                          {
                            row.channel
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row.spend
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row
                              .attributed_revenue
                          )
                        }
                      </td>

                      <td>
                        {
                          row
                            .roas
                            .toFixed(2)
                        }x
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row.cac
                          )
                        }
                      </td>

                      <td>
                        {
                          formatNumber(
                            row.orders
                          )
                        }
                      </td>

                      <td>
                        {
                          row
                            .session_conversion_percent
                            .toFixed(2)
                        }%
                      </td>

                    </tr>
                  )
                )
              }

            </tbody>

          </table>

        </div>

      </section>


      <section className="pl-attribution-note">

        <BarChart3
          size={20}
        />

        <div>

          <strong>
            Attribution scope
          </strong>

          <p>
            Marketing attribution is currently
            aggregate campaign-level data.
            ProfitLens does not claim order-level
            attribution or SKU-level marketing
            profitability until deterministic
            allocation is available.
          </p>

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

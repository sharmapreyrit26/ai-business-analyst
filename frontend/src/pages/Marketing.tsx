import {
  useEffect,
  useState,
} from 'react'

import {
  AlertTriangle,
  BadgeIndianRupee,
  BarChart3,
  MousePointerClick,
  Target,
  TrendingUp,
  Users,
} from 'lucide-react'

import {
  api,
} from '../api/profitlens'

import type {
  D2CMarketingCampaignRow,
  D2CMarketingChannelRow,
  D2CMarketingInsightsResponse,
  D2CMarketingSummaryResponse,
  D2CMarketingTrendRow,
} from '../types/api'


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
  ).format(value)
}


function formatNumber(
  value: number
) {
  return new Intl.NumberFormat(
    'en-IN'
  ).format(value)
}


export default function Marketing({
  month,
}: MarketingProps) {
  const [
    summary,
    setSummary,
  ] = useState<D2CMarketingSummaryResponse | null>(
    null
  )

  const [
    channels,
    setChannels,
  ] = useState<D2CMarketingChannelRow[]>(
    []
  )

  const [
    campaigns,
    setCampaigns,
  ] = useState<D2CMarketingCampaignRow[]>(
    []
  )

  const [
    trend,
    setTrend,
  ] = useState<D2CMarketingTrendRow[]>(
    []
  )

  const [
    insights,
    setInsights,
  ] = useState<D2CMarketingInsightsResponse | null>(
    null
  )

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  )


  useEffect(
    () => {
      let cancelled = false

      setLoading(true)
      setError(null)

      Promise.all([
        api.marketing(month),
        api.marketingChannels(month),
        api.marketingCampaigns(month),
        api.marketingTrend(),
        api.marketingInsights(month),
      ])
        .then(
          ([
            summaryResponse,
            channelResponse,
            campaignResponse,
            trendResponse,
            insightsResponse,
          ]) => {
            if (cancelled) {
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
          (
            requestError
          ) => {
            if (cancelled) {
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
                : 'Could not load marketing analytics.'
            )
          }
        )
        .finally(
          () => {
            if (!cancelled) {
              setLoading(false)
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


  if (loading) {
    return (
      <div className="page">
        <div className="card">
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
      <div className="page">
        <div className="card error-card">
          <AlertTriangle size={20} />

          <div>
            <strong>
              Could not load marketing
            </strong>

            <p>
              {
                error
                || 'Unknown error'
              }
            </p>
          </div>
        </div>
      </div>
    )
  }


  return (
    <div className="page">

      <div className="page-header">
        <div>
          <div className="eyebrow">
            Marketing analytics
          </div>

          <h2>
            Marketing Performance
          </h2>

          <p>
            Spend efficiency, ROAS, CAC,
            channels and campaigns for {month}.
          </p>
        </div>
      </div>


      <div className="metric-grid">

        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Marketing Spend
              </div>

              <div className="metric-value">
                {
                  formatCurrency(
                    summary.marketing_spend
                  )
                }
              </div>
            </div>

            <div className="metric-icon">
              <BadgeIndianRupee
                size={20}
              />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Attributed Revenue
              </div>

              <div className="metric-value">
                {
                  formatCurrency(
                    summary.attributed_revenue
                  )
                }
              </div>
            </div>

            <div className="metric-icon">
              <TrendingUp
                size={20}
              />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Blended ROAS
              </div>

              <div className="metric-value">
                {
                  summary
                    .blended_roas
                    .toFixed(2)
                }x
              </div>
            </div>

            <div className="metric-icon">
              <Target
                size={20}
              />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                CAC
              </div>

              <div className="metric-value">
                {
                  formatCurrency(
                    summary.cac
                  )
                }
              </div>
            </div>

            <div className="metric-icon">
              <Users
                size={20}
              />
            </div>
          </div>

          <div className="metric-subtitle">
            {
              formatNumber(
                summary.new_customers
              )
            } attributed new customers
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Cost / Order
          </div>

          <div className="metric-value">
            {
              formatCurrency(
                summary.cost_per_order
              )
            }
          </div>

          <div className="metric-subtitle">
            {
              formatNumber(
                summary.attributed_orders
              )
            } attributed orders
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Conversion Rate
              </div>

              <div className="metric-value">
                {
                  summary
                    .session_conversion_percent
                    .toFixed(2)
                }%
              </div>
            </div>

            <div className="metric-icon">
              <MousePointerClick
                size={20}
              />
            </div>
          </div>
        </div>

      </div>


      <div className="section-heading">
        <div>
          <h2>
            Marketing Signals
          </h2>

          <p>
            Deterministic channel-level highlights.
          </p>
        </div>
      </div>


      <div className="metric-grid">

        <div className="card metric-card">
          <div className="metric-label">
            Best ROAS Channel
          </div>

          <div className="metric-value">
            {
              insights
                ?.best_roas_channel
                ?.channel
              || 'N/A'
            }
          </div>

          <div className="metric-subtitle">
            {
              insights
                ?.best_roas_channel
              ? `${insights
                  .best_roas_channel
                  .roas
                  .toFixed(2)}x ROAS`
              : 'No paid channel available'
            }
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Lowest CAC Channel
          </div>

          <div className="metric-value">
            {
              insights
                ?.lowest_cac_channel
                ?.channel
              || 'N/A'
            }
          </div>

          <div className="metric-subtitle">
            {
              insights
                ?.lowest_cac_channel
              ? formatCurrency(
                  insights
                    .lowest_cac_channel
                    .cac
                )
              : 'Not available'
            }
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Highest Revenue Channel
          </div>

          <div className="metric-value">
            {
              insights
                ?.highest_revenue_channel
                ?.channel
              || 'N/A'
            }
          </div>

          <div className="metric-subtitle">
            {
              insights
                ?.highest_revenue_channel
              ? formatCurrency(
                  insights
                    .highest_revenue_channel
                    .attributed_revenue
                )
              : 'Not available'
            }
          </div>
        </div>

      </div>


      <div className="section-heading">
        <div>
          <h2>
            Channel Performance
          </h2>

          <p>
            Spend, revenue and acquisition
            efficiency by channel.
          </p>
        </div>
      </div>


      <div className="card">
        <div className="table-wrap">
          <table className="data-table">

            <thead>
              <tr>
                <th>Channel</th>
                <th>Spend</th>
                <th>Revenue</th>
                <th>ROAS</th>
                <th>CAC</th>
                <th>Orders</th>
                <th>New Customers</th>
                <th>Conversion</th>
              </tr>
            </thead>

            <tbody>
              {
                channels.map(
                  (
                    row
                  ) => (
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
                            row.attributed_revenue
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
                          formatNumber(
                            row.new_customers
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
      </div>


      <div className="section-heading">
        <div>
          <h2>
            Campaign Performance
          </h2>

          <p>
            Campaign-level acquisition economics.
          </p>
        </div>
      </div>


      <div className="card">
        <div className="table-wrap">
          <table className="data-table">

            <thead>
              <tr>
                <th>Campaign</th>
                <th>Channel</th>
                <th>Spend</th>
                <th>Revenue</th>
                <th>ROAS</th>
                <th>CAC</th>
                <th>Orders</th>
                <th>Conversion</th>
              </tr>
            </thead>

            <tbody>
              {
                campaigns.map(
                  (
                    row,
                    index,
                  ) => (
                    <tr
                      key={
                        `${row.channel}-${row.campaign}-${index}`
                      }
                    >
                      <td>
                        <strong>
                          {
                            row.campaign
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          row.channel
                        }
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
                            row.attributed_revenue
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
      </div>


      <div className="section-heading">
        <div>
          <h2>
            Monthly Trend
          </h2>

          <p>
            Marketing efficiency across the
            available reporting period.
          </p>
        </div>
      </div>


      <div className="card">
        <div className="table-wrap">
          <table className="data-table">

            <thead>
              <tr>
                <th>Month</th>
                <th>Spend</th>
                <th>Revenue</th>
                <th>ROAS</th>
                <th>CAC</th>
                <th>Orders</th>
                <th>Spend Growth</th>
                <th>ROAS Change</th>
              </tr>
            </thead>

            <tbody>
              {
                trend.map(
                  (
                    row
                  ) => (
                    <tr
                      key={
                        row.month
                      }
                    >
                      <td>
                        <strong>
                          {
                            row.month
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
                            row.attributed_revenue
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
                            .spend_growth_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          row
                            .roas_change_percent
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
      </div>


      <div className="card limitation-card">
        <div>
          <strong>
            Attribution scope
          </strong>

          <p>
            Marketing attribution is currently
            aggregate campaign-level data. It is not
            joined to individual order IDs, so ProfitLens
            does not claim order-level attribution or
            SKU-level marketing profitability.
          </p>
        </div>

        <BarChart3 size={20} />
      </div>

    </div>
  )
}
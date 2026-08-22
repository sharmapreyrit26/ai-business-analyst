import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowRight,
  RefreshCcw,
  Repeat2,
  RotateCcw,
  ShoppingCart,
  Sparkles,
  Users,
  WalletCards,
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
  D2CAcquisitionChannelRow,
  D2CCustomerCohortRow,
  D2CCustomerSummaryResponse,
} from '../types/api'

import type {
  MetricContract,
  MetricSentiment,
  MetricUnit,
} from '../types/metric'


type CustomersProps = {
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


function buildMetric(
  input: {
    metricId: string
    label: string
    value: number
    formattedValue: string
    unit: MetricUnit
    higherIsBetter: boolean
    definition?: string
  }
): MetricContract {
  const sentiment:
    MetricSentiment =
      'neutral'

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
        null,

      direction:
        'unknown',
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

    metadata: {
      higher_is_better:
        input.higherIsBetter,
    },
  }
}


export default function Customers({
  month,
}: CustomersProps) {
  const navigate =
    useNavigate()

  const drilldown =
    useMetricDrilldown()

  const [
    summary,
    setSummary,
  ] = useState<
    D2CCustomerSummaryResponse | null
  >(
    null
  )

  const [
    channels,
    setChannels,
  ] = useState<
    D2CAcquisitionChannelRow[]
  >(
    []
  )

  const [
    cohorts,
    setCohorts,
  ] = useState<
    D2CCustomerCohortRow[]
  >(
    []
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
        api.customers(
          month
        ),

        api.acquisitionChannels(
          month
        ),

        api.customerCohorts(),
      ])
        .then(
          ([
            summaryResponse,
            channelResponse,
            cohortResponse,
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

            setCohorts(
              cohortResponse.data
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
            setCohorts([])

            setError(
              requestError
                instanceof Error
                ? requestError.message
                : (
                    'Could not load '
                    + 'customer analytics.'
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


  const selectedMonthCohorts =
    useMemo(
      () =>
        cohorts
          .filter(
            row =>
              row.cohort_month
              === month
          )
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              first
                .months_since_first_order
              - second
                .months_since_first_order
          ),
      [
        cohorts,
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
              'active_customers',

            label:
              'Active Customers',

            value:
              summary
                .active_customers,

            formattedValue:
              formatNumber(
                summary
                  .active_customers
              ),

            unit:
              'count',

            higherIsBetter:
              true,

            definition:
              'Customers with activity in the selected reporting period.',
          }),

          buildMetric({
            metricId:
              'repeat_customer_rate_percent',

            label:
              'Repeat Customer Rate',

            value:
              summary
                .repeat_customer_rate_percent,

            formattedValue:
              `${summary
                .repeat_customer_rate_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              true,
          }),

          buildMetric({
            metricId:
              'orders_per_customer',

            label:
              'Orders Per Customer',

            value:
              summary
                .orders_per_customer,

            formattedValue:
              summary
                .orders_per_customer
                .toFixed(2),

            unit:
              'ratio',

            higherIsBetter:
              true,
          }),

          buildMetric({
            metricId:
              'rto_rate_percent',

            label:
              'Customer RTO Rate',

            value:
              summary
                .rto_rate_percent,

            formattedValue:
              `${summary
                .rto_rate_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              false,
          }),

          buildMetric({
            metricId:
              'return_rate_percent',

            label:
              'Return Rate',

            value:
              summary
                .return_rate_percent,

            formattedValue:
              `${summary
                .return_rate_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              false,
          }),

          buildMetric({
            metricId:
              'cod_share_percent',

            label:
              'COD Share',

            value:
              summary
                .cod_share_percent,

            formattedValue:
              `${summary
                .cod_share_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              false,
          }),
        ]
      },
      [
        summary,
      ]
    )


  const topAcquisitionChannels =
    useMemo(
      () =>
        channels
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second.customers
              - first.customers
          )
          .slice(
            0,
            5
          ),
      [
        channels,
      ]
    )


  const bestQualityChannels =
    useMemo(
      () =>
        channels
          .slice()
          .sort(
            (
              first,
              second,
            ) => {
              if (
                first.rto_rate_percent
                !== second.rto_rate_percent
              ) {
                return (
                  first.rto_rate_percent
                  - second.rto_rate_percent
                )
              }

              return (
                first.return_rate_percent
                - second.return_rate_percent
              )
            }
          )
          .slice(
            0,
            4
          ),
      [
        channels,
      ]
    )


  const riskiestChannels =
    useMemo(
      () =>
        channels
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              (
                second.rto_rate_percent
                + second.return_rate_percent
              )
              - (
                  first.rto_rate_percent
                  + first.return_rate_percent
                )
          )
          .slice(
            0,
            4
          ),
      [
        channels,
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
      <div className="pl-customers-v2">

        <div className="pl-page-state">

          <RefreshCcw
            size={20}
          />

          Loading customer analytics...

        </div>

      </div>
    )
  }


  if (
    error
    || !summary
  ) {
    return (
      <div className="pl-customers-v2">

        <div className="pl-page-state error">

          <AlertTriangle
            size={20}
          />

          <div>
            <strong>
              Could not load customers
            </strong>

            <span>
              {
                error
                ?? 'Customer data is unavailable.'
              }
            </span>
          </div>

        </div>

      </div>
    )
  }


  return (
    <div className="pl-customers-v2">

      <section className="pl-business-hero">

        <div>

          <div className="pl-page-eyebrow">
            Customer intelligence
          </div>

          <h1>
            Customer Analysis
          </h1>

          <p>
            Understand repeat behaviour,
            acquisition quality and customer
            risk for {month}.
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
            Test growth scenario

            <ArrowRight
              size={14}
            />
          </button>

        </div>

      </section>


      <section className="pl-customer-strip">

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

          <Repeat2
            size={17}
          />

          <span>
            Repeat Customers
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .repeat_customers
              )
            }
          </strong>

        </div>


        <div>

          <ShoppingCart
            size={17}
          />

          <span>
            Orders
          </span>

          <strong>
            {
              formatNumber(
                summary.orders
              )
            }
          </strong>

        </div>


        <div>

          <WalletCards
            size={17}
          />

          <span>
            COD Orders
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .cod_orders
              )
            }
          </strong>

        </div>

      </section>


      <section>

        <div className="pl-section-header">

          <div>

            <h2>
              Customer health
            </h2>

            <p>
              Core repeat, engagement and
              customer-risk metrics.
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


      <section className="pl-customer-analysis-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Acquisition mix
              </span>

              <h2>
                Customer volume by channel
              </h2>

            </div>

          </div>


          <div className="pl-customer-channel-list">

            {
              topAcquisitionChannels.map(
                row => (
                  <div
                    key={
                      row.acquisition_channel
                    }
                    className="pl-customer-channel-row"
                  >

                    <div>

                      <strong>
                        {
                          row
                            .acquisition_channel
                        }
                      </strong>

                      <span>
                        {
                          formatNumber(
                            row.customers
                          )
                        } customers
                      </span>

                    </div>


                    <div>

                      <strong>
                        {
                          formatCurrency(
                            row.average_order_value
                          )
                        }
                      </strong>

                      <span>
                        AOV
                      </span>

                    </div>


                    <div>

                      <strong>
                        {
                          row
                            .orders_per_customer
                            .toFixed(2)
                        }
                      </strong>

                      <span>
                        Orders / customer
                      </span>

                    </div>


                    <div>

                      <strong>
                        {
                          formatCurrency(
                            row.order_value
                          )
                        }
                      </strong>

                      <span>
                        Placed value
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
                Acquisition quality
              </span>

              <h2>
                Lowest fulfillment risk
              </h2>

            </div>

          </div>


          <div className="pl-customer-quality-list">

            {
              bestQualityChannels.map(
                row => (
                  <div
                    key={
                      row.acquisition_channel
                    }
                    className="pl-customer-quality-row"
                  >

                    <strong>
                      {
                        row
                          .acquisition_channel
                      }
                    </strong>

                    <div>
                      <span>
                        RTO
                      </span>

                      <strong>
                        {
                          row
                            .rto_rate_percent
                            .toFixed(2)
                        }%
                      </strong>
                    </div>

                    <div>
                      <span>
                        Returns
                      </span>

                      <strong>
                        {
                          row
                            .return_rate_percent
                            .toFixed(2)
                        }%
                      </strong>
                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>

      </section>


      <section className="pl-customer-analysis-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Risk watch
              </span>

              <h2>
                Channels to review
              </h2>

            </div>

          </div>


          <div className="pl-customer-quality-list">

            {
              riskiestChannels.map(
                row => (
                  <div
                    key={
                      row.acquisition_channel
                    }
                    className="pl-customer-quality-row risk"
                  >

                    <strong>
                      {
                        row
                          .acquisition_channel
                      }
                    </strong>

                    <div>
                      <span>
                        RTO
                      </span>

                      <strong>
                        {
                          row
                            .rto_rate_percent
                            .toFixed(2)
                        }%
                      </strong>
                    </div>

                    <div>
                      <span>
                        Returns
                      </span>

                      <strong>
                        {
                          row
                            .return_rate_percent
                            .toFixed(2)
                        }%
                      </strong>
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
                Observed retention
              </span>

              <h2>
                Cohort retention
              </h2>

            </div>

          </div>


          {
            selectedMonthCohorts.length
            > 0
              ? (
                <div className="pl-customer-retention">

                  {
                    selectedMonthCohorts.map(
                      row => (
                        <div
                          key={
                            row
                              .months_since_first_order
                          }
                          className="pl-retention-row"
                        >

                          <div>

                            <strong>
                              M{
                                row
                                  .months_since_first_order
                              }
                            </strong>

                            <span>
                              {
                                formatNumber(
                                  row
                                    .active_customers
                                )
                              } active
                            </span>

                          </div>


                          <div className="pl-retention-track">

                            <i
                              style={{
                                width:
                                  `${Math.max(
                                    0,
                                    Math.min(
                                      100,
                                      row
                                        .retention_percent
                                    )
                                  )}%`,
                              }}
                            />

                          </div>


                          <strong>
                            {
                              row
                                .retention_percent
                                .toFixed(2)
                            }%
                          </strong>

                        </div>
                      )
                    )
                  }

                </div>
              )
              : (
                <div className="pl-empty-panel">
                  No later retention periods
                  are observable for this cohort yet.
                </div>
              )
          }

        </div>

      </section>


      <section className="pl-founder-panel">

        <div className="pl-panel-header">

          <div>

            <span className="pl-page-eyebrow">
              Detailed acquisition economics
            </span>

            <h2>
              Acquisition channel comparison
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
                  Customers
                </th>

                <th>
                  Orders
                </th>

                <th>
                  Order Value
                </th>

                <th>
                  AOV
                </th>

                <th>
                  Orders / Customer
                </th>

                <th>
                  RTO
                </th>

                <th>
                  Returns
                </th>
              </tr>
            </thead>

            <tbody>

              {
                channels.map(
                  row => (
                    <tr
                      key={
                        row
                          .acquisition_channel
                      }
                    >

                      <td>
                        <strong>
                          {
                            row
                              .acquisition_channel
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          formatNumber(
                            row.customers
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
                          formatCurrency(
                            row.order_value
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row
                              .average_order_value
                          )
                        }
                      </td>

                      <td>
                        {
                          row
                            .orders_per_customer
                            .toFixed(2)
                        }
                      </td>

                      <td>
                        {
                          row
                            .rto_rate_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          row
                            .return_rate_percent
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


      <section className="pl-customer-scope-note">

        <RotateCcw
          size={20}
        />

        <div>

          <strong>
            Customer metric scope
          </strong>

          <p>
            Acquisition-channel order value
            represents placed-order economics,
            not realized revenue. Cohort retention
            is observed historical behaviour and
            is not predictive LTV or churn.
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

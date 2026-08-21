import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  Repeat2,
  RotateCcw,
  ShoppingCart,
  Users,
  WalletCards,
} from 'lucide-react'

import {
  api,
} from '../api/profitlens'

import type {
  D2CAcquisitionChannelRow,
  D2CCustomerCohortRow,
  D2CCustomerSummaryResponse,
} from '../types/api'


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


export default function Customers({
  month,
}: CustomersProps) {
  const [
    summary,
    setSummary,
  ] = useState<D2CCustomerSummaryResponse | null>(
    null
  )

  const [
    channels,
    setChannels,
  ] = useState<D2CAcquisitionChannelRow[]>(
    []
  )

  const [
    cohorts,
    setCohorts,
  ] = useState<D2CCustomerCohortRow[]>(
    []
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
        api.customers(month),
        api.acquisitionChannels(month),
        api.customerCohorts(),
      ])
        .then(
          ([
            summaryResponse,
            channelResponse,
            cohortResponse,
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

            setCohorts(
              cohortResponse.data
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
            setCohorts([])

            setError(
              requestError
                instanceof Error
                ? requestError.message
                : 'Could not load customer analytics.'
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


  const selectedMonthCohorts =
    useMemo(
      () => {
        return cohorts.filter(
          (
            row
          ) =>
            row.cohort_month
            === month
        )
      },
      [
        cohorts,
        month,
      ]
    )


  if (loading) {
    return (
      <div className="page">
        <div className="card">
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
      <div className="page">
        <div className="card error-card">
          <AlertTriangle size={20} />

          <div>
            <strong>
              Could not load customers
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
            Customer analytics
          </div>

          <h2>
            Customer Performance
          </h2>

          <p>
            Acquisition, repeat behaviour,
            RTO and customer quality for {month}.
          </p>
        </div>
      </div>


      <div className="metric-grid">

        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Active Customers
              </div>

              <div className="metric-value">
                {
                  formatNumber(
                    summary.active_customers
                  )
                }
              </div>
            </div>

            <div className="metric-icon">
              <Users size={20} />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                New Customers
              </div>

              <div className="metric-value">
                {
                  formatNumber(
                    summary.new_customers
                  )
                }
              </div>
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Repeat Customers
              </div>

              <div className="metric-value">
                {
                  formatNumber(
                    summary.repeat_customers
                  )
                }
              </div>
            </div>

            <div className="metric-icon">
              <Repeat2 size={20} />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Repeat Rate
              </div>

              <div className="metric-value">
                {
                  summary
                    .repeat_customer_rate_percent
                    .toFixed(2)
                }%
              </div>
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Orders / Customer
              </div>

              <div className="metric-value">
                {
                  summary
                    .orders_per_customer
                    .toFixed(2)
                }
              </div>
            </div>

            <div className="metric-icon">
              <ShoppingCart size={20} />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                COD Share
              </div>

              <div className="metric-value">
                {
                  summary
                    .cod_share_percent
                    .toFixed(2)
                }%
              </div>
            </div>

            <div className="metric-icon">
              <WalletCards size={20} />
            </div>
          </div>
        </div>

      </div>


      <div className="metric-grid">

        <div className="card metric-card">
          <div className="metric-label">
            RTO Rate
          </div>

          <div className="metric-value">
            {
              summary
                .rto_rate_percent
                .toFixed(2)
            }%
          </div>

          <div className="metric-subtitle">
            {
              formatNumber(
                summary.rto_orders
              )
            } RTO orders
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Return Rate
          </div>

          <div className="metric-value">
            {
              summary
                .return_rate_percent
                .toFixed(2)
            }%
          </div>

          <div className="metric-subtitle">
            {
              formatNumber(
                summary.returned_orders
              )
            } returned orders
          </div>

          <RotateCcw size={18} />
        </div>

      </div>


      <div className="section-heading">
        <div>
          <h2>
            Acquisition Channel Quality
          </h2>

          <p>
            Customer volume and placed-order
            behaviour by acquisition channel.
          </p>
        </div>
      </div>


      <div className="card">
        <div className="table-wrap">
          <table className="data-table">

            <thead>
              <tr>
                <th>Channel</th>
                <th>Customers</th>
                <th>Orders</th>
                <th>Order Value</th>
                <th>AOV</th>
                <th>Orders / Customer</th>
                <th>RTO</th>
                <th>Returns</th>
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
                        row.acquisition_channel
                      }
                    >
                      <td>
                        <strong>
                          {
                            row.acquisition_channel
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
                            row.average_order_value
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
      </div>


      <div className="section-heading">
        <div>
          <h2>
            Cohort Retention
          </h2>

          <p>
            Observed retention for customers
            first acquired in {month}.
          </p>
        </div>
      </div>


      <div className="card">
        {
          selectedMonthCohorts.length > 0
            ? (
              <div className="table-wrap">
                <table className="data-table">

                  <thead>
                    <tr>
                      <th>
                        Months Since First Order
                      </th>

                      <th>
                        Cohort Size
                      </th>

                      <th>
                        Active Customers
                      </th>

                      <th>
                        Retention
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {
                      selectedMonthCohorts.map(
                        (
                          row
                        ) => (
                          <tr
                            key={
                              row
                                .months_since_first_order
                            }
                          >
                            <td>
                              {
                                row
                                  .months_since_first_order
                              }
                            </td>

                            <td>
                              {
                                formatNumber(
                                  row.cohort_size
                                )
                              }
                            </td>

                            <td>
                              {
                                formatNumber(
                                  row.active_customers
                                )
                              }
                            </td>

                            <td>
                              {
                                row
                                  .retention_percent
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
            )
            : (
              <div className="empty-state">
                No later retention periods
                are observable for this cohort yet.
              </div>
            )
        }
      </div>


      <div className="card limitation-card">
        <strong>
          Customer metric scope
        </strong>

        <p>
          Acquisition-channel order value represents
          placed-order economics, not realized revenue.
          Cohort retention is observed historical
          behaviour and is not predictive LTV or churn.
        </p>
      </div>

    </div>
  )
}
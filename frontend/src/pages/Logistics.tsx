import {
  useEffect,
  useState,
} from 'react'

import {
  AlertTriangle,
  RotateCcw,
  Truck,
  WalletCards,
} from 'lucide-react'

import {
  api,
} from '../api/profitlens'

import type {
  D2CCourierRow,
  D2CLogisticsSummaryResponse,
  D2CPaymentLogisticsRow,
  D2CZoneRow,
} from '../types/api'


type LogisticsProps = {
  month: string
}


function formatNumber(
  value: number
) {
  return new Intl.NumberFormat(
    'en-IN'
  ).format(value)
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


export default function Logistics({
  month,
}: LogisticsProps) {
  const [
    summaryData,
    setSummaryData,
  ] = useState<D2CLogisticsSummaryResponse | null>(
    null
  )

  const [
    couriers,
    setCouriers,
  ] = useState<D2CCourierRow[]>(
    []
  )

  const [
    paymentGroups,
    setPaymentGroups,
  ] = useState<D2CPaymentLogisticsRow[]>(
    []
  )

  const [
    zones,
    setZones,
  ] = useState<D2CZoneRow[]>(
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
        api.logistics(month),
        api.couriers(month),
        api.paymentLogistics(month),
        api.zones(month),
      ])
        .then(
          ([
            logisticsResponse,
            courierResponse,
            paymentResponse,
            zoneResponse,
          ]) => {
            if (cancelled) {
              return
            }

            setSummaryData(
              logisticsResponse
            )

            setCouriers(
              courierResponse.data
            )

            setPaymentGroups(
              paymentResponse.data
            )

            setZones(
              zoneResponse.data
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

            setSummaryData(null)
            setCouriers([])
            setPaymentGroups([])
            setZones([])

            setError(
              requestError
                instanceof Error
                ? requestError.message
                : 'Could not load logistics analytics.'
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
          Loading logistics analytics...
        </div>
      </div>
    )
  }


  if (
    error
    || !summaryData
  ) {
    return (
      <div className="page">
        <div className="card error-card">
          <AlertTriangle size={20} />

          <div>
            <strong>
              Could not load logistics
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


  const {
    summary,
  } = summaryData


  return (
    <div className="page">

      <div className="page-header">
        <div>
          <div className="eyebrow">
            Logistics analytics
          </div>

          <h2>
            Logistics Performance
          </h2>

          <p>
            Delivery, RTO, NDR, courier
            and zone performance for {month}.
          </p>
        </div>
      </div>


      <div className="metric-grid">

        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Total Orders
              </div>

              <div className="metric-value">
                {
                  formatNumber(
                    summary.total_orders
                  )
                }
              </div>
            </div>

            <div className="metric-icon">
              <Truck size={20} />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Delivery Rate
              </div>

              <div className="metric-value">
                {
                  summary
                    .delivery_rate_percent
                    .toFixed(2)
                }%
              </div>
            </div>
          </div>

          <div className="metric-subtitle">
            {
              formatNumber(
                summary.delivered_orders
              )
            } orders with delivery timestamp
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
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
            </div>

            <div className="metric-icon">
              <RotateCcw size={20} />
            </div>
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
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                NDR Rate
              </div>

              <div className="metric-value">
                {
                  summary
                    .ndr_rate_percent
                    .toFixed(2)
                }%
              </div>
            </div>

            <div className="metric-icon">
              <AlertTriangle size={20} />
            </div>
          </div>

          <div className="metric-subtitle">
            {
              formatNumber(
                summary.ndr_orders
              )
            } NDR orders
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            On-Time Delivery
          </div>

          <div className="metric-value">
            {
              summary
                .on_time_delivery_percent
                .toFixed(2)
            }%
          </div>

          <div className="metric-subtitle">
            {
              formatNumber(
                summary.on_time_orders
              )
            } on-time / {
              formatNumber(
                summary.promise_measured_orders
              )
            } measurable
          </div>
        </div>


        <div className="card metric-card">
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

          <div className="metric-subtitle">
            {
              formatNumber(
                summary.cod_orders
              )
            } COD orders
          </div>

          <WalletCards size={18} />
        </div>

      </div>


      <div className="section-heading">
        <div>
          <h2>
            Delivery TAT
          </h2>

          <p>
            Fulfilment speed and tail performance.
          </p>
        </div>
      </div>


      <div className="metric-grid">

        <div className="card metric-card">
          <div className="metric-label">
            Average Delivery TAT
          </div>

          <div className="metric-value">
            {
              summary
                .average_delivery_tat_days
                .toFixed(2)
            } days
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Median Delivery TAT
          </div>

          <div className="metric-value">
            {
              summary
                .median_delivery_tat_days
                .toFixed(2)
            } days
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            P90 Delivery TAT
          </div>

          <div className="metric-value">
            {
              summary
                .p90_delivery_tat_days
                .toFixed(2)
            } days
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Average First Attempt
          </div>

          <div className="metric-value">
            {
              summary
                .average_first_attempt_tat_days
                .toFixed(2)
            } days
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            P90 First Attempt
          </div>

          <div className="metric-value">
            {
              summary
                .p90_first_attempt_tat_days
                .toFixed(2)
            } days
          </div>
        </div>

      </div>


      <div className="section-heading">
        <div>
          <h2>
            Courier Performance
          </h2>

          <p>
            Compare courier delivery speed,
            RTO, NDR and commercial rates.
          </p>
        </div>
      </div>


      <div className="card">
        <div className="table-wrap">
          <table className="data-table">

            <thead>
              <tr>
                <th>Courier</th>
                <th>Orders</th>
                <th>Delivery Rate</th>
                <th>RTO</th>
                <th>NDR</th>
                <th>Avg TAT</th>
                <th>P90 TAT</th>
                <th>On-Time</th>
                <th>Base Cost</th>
                <th>RTO Fee</th>
              </tr>
            </thead>

            <tbody>
              {
                couriers.map(
                  (
                    row
                  ) => (
                    <tr
                      key={
                        row.courier_name
                      }
                    >
                      <td>
                        <strong>
                          {
                            row.courier_name
                          }
                        </strong>
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
                            .delivery_rate_percent
                            .toFixed(2)
                        }%
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
                            .ndr_rate_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          row
                            .average_delivery_tat_days
                            .toFixed(2)
                        }
                      </td>

                      <td>
                        {
                          row
                            .p90_delivery_tat_days
                            .toFixed(2)
                        }
                      </td>

                      <td>
                        {
                          row
                            .on_time_delivery_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row.base_shipping_cost
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row.rto_fee
                          )
                        }
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
            COD vs Prepaid
          </h2>

          <p>
            Operational quality by payment type.
          </p>
        </div>
      </div>


      <div className="card">
        <div className="table-wrap">
          <table className="data-table">

            <thead>
              <tr>
                <th>Payment</th>
                <th>Orders</th>
                <th>RTO</th>
                <th>NDR</th>
                <th>Returns</th>
                <th>Avg TAT</th>
                <th>P90 TAT</th>
              </tr>
            </thead>

            <tbody>
              {
                paymentGroups.map(
                  (
                    row
                  ) => (
                    <tr
                      key={
                        row.payment_group
                      }
                    >
                      <td>
                        <strong>
                          {
                            row.payment_group
                          }
                        </strong>
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
                            .rto_rate_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          row
                            .ndr_rate_percent
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

                      <td>
                        {
                          row
                            .average_delivery_tat_days
                            .toFixed(2)
                        }
                      </td>

                      <td>
                        {
                          row
                            .p90_delivery_tat_days
                            .toFixed(2)
                        }
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
            Zone Risk
          </h2>

          <p>
            Delivery risk and speed by shipping zone.
          </p>
        </div>
      </div>


      <div className="card">
        <div className="table-wrap">
          <table className="data-table">

            <thead>
              <tr>
                <th>Zone</th>
                <th>Orders</th>
                <th>RTO</th>
                <th>NDR</th>
                <th>Avg TAT</th>
                <th>P90 TAT</th>
              </tr>
            </thead>

            <tbody>
              {
                zones.map(
                  (
                    row
                  ) => (
                    <tr
                      key={
                        row.zone
                      }
                    >
                      <td>
                        <strong>
                          {
                            row.zone
                          }
                        </strong>
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
                            .rto_rate_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          row
                            .ndr_rate_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          row
                            .average_delivery_tat_days
                            .toFixed(2)
                        }
                      </td>

                      <td>
                        {
                          row
                            .p90_delivery_tat_days
                            .toFixed(2)
                        }
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
        <strong>
          Logistics metric scope
        </strong>

        <p>
          Delivery rate represents orders with a recorded
          customer-delivery timestamp. On-time delivery is
          calculated only where both delivery and promised
          delivery dates are measurable.
        </p>
      </div>

    </div>
  )
}
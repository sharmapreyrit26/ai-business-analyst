import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowRight,
  Clock3,
  PackageCheck,
  RefreshCcw,
  RotateCcw,
  Sparkles,
  Truck,
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
  D2CCourierRow,
  D2CLogisticsSummaryResponse,
  D2CPaymentLogisticsRow,
  D2CZoneRow,
} from '../types/api'

import type {
  MetricContract,
  MetricUnit,
} from '../types/metric'


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

    sentiment:
      'neutral',

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


export default function Logistics({
  month,
}: LogisticsProps) {
  const navigate =
    useNavigate()

  const drilldown =
    useMetricDrilldown()

  const [
    summaryData,
    setSummaryData,
  ] = useState<
    D2CLogisticsSummaryResponse | null
  >(null)

  const [
    couriers,
    setCouriers,
  ] = useState<
    D2CCourierRow[]
  >([])

  const [
    paymentGroups,
    setPaymentGroups,
  ] = useState<
    D2CPaymentLogisticsRow[]
  >([])

  const [
    zones,
    setZones,
  ] = useState<
    D2CZoneRow[]
  >([])

  const [
    loading,
    setLoading,
  ] = useState(true)

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

      Promise.all([
        api.logistics(
          month
        ),

        api.couriers(
          month
        ),

        api.paymentLogistics(
          month
        ),

        api.zones(
          month
        ),
      ])
        .then(
          ([
            logisticsResponse,
            courierResponse,
            paymentResponse,
            zoneResponse,
          ]) => {
            if (
              cancelled
            ) {
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
          requestError => {
            if (
              cancelled
            ) {
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
                : (
                    'Could not load '
                    + 'logistics analytics.'
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


  const summary =
    summaryData
      ?.summary
    ?? null


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
              'delivery_rate_percent',

            label:
              'Delivery Rate',

            value:
              summary
                .delivery_rate_percent,

            formattedValue:
              `${summary
                .delivery_rate_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              true,

            definition:
              'Share of orders with a recorded customer-delivery timestamp.',
          }),

          buildMetric({
            metricId:
              'rto_rate_percent',

            label:
              'RTO Rate',

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
              'ndr_rate_percent',

            label:
              'NDR Rate',

            value:
              summary
                .ndr_rate_percent,

            formattedValue:
              `${summary
                .ndr_rate_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              false,
          }),

          buildMetric({
            metricId:
              'on_time_delivery_percent',

            label:
              'On-Time Delivery',

            value:
              summary
                .on_time_delivery_percent,

            formattedValue:
              `${summary
                .on_time_delivery_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              true,

            definition:
              'Share of measurable delivered orders delivered on or before promised date.',
          }),

          buildMetric({
            metricId:
              'late_delivery_percent',

            label:
              'Late Delivery',

            value:
              summary
                .late_delivery_percent,

            formattedValue:
              `${summary
                .late_delivery_percent
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
        ]
      },
      [
        summary,
      ]
    )


  const fastestCouriers =
    useMemo(
      () =>
        couriers
          .filter(
            row =>
              row.courier_name
              !== 'Unknown'
          )
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              first
                .average_delivery_tat_days
              - second
                .average_delivery_tat_days
          ),
      [
        couriers,
      ]
    )


  const courierRisk =
    useMemo(
      () =>
        couriers
          .filter(
            row =>
              row.courier_name
              !== 'Unknown'
          )
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second
                .rto_rate_percent
              - first
                .rto_rate_percent
          ),
      [
        couriers,
      ]
    )


  const zoneRisk =
    useMemo(
      () =>
        zones
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second
                .rto_rate_percent
              - first
                .rto_rate_percent
          ),
      [
        zones,
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
      <div className="pl-logistics-v2">

        <div className="pl-page-state">

          <RefreshCcw
            size={20}
          />

          Loading logistics analytics...

        </div>

      </div>
    )
  }


  if (
    error
    || !summary
  ) {
    return (
      <div className="pl-logistics-v2">

        <div className="pl-page-state error">

          <AlertTriangle
            size={20}
          />

          <div>

            <strong>
              Could not load logistics
            </strong>

            <span>
              {
                error
                ?? 'Logistics data is unavailable.'
              }
            </span>

          </div>

        </div>

      </div>
    )
  }


  return (
    <div className="pl-logistics-v2">

      <section className="pl-business-hero">

        <div>

          <div className="pl-page-eyebrow">
            Operations intelligence
          </div>

          <h1>
            Logistics Performance
          </h1>

          <p>
            Monitor delivery quality, RTO,
            NDR, courier performance and
            operational risk for {month}.
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

            Test RTO scenario

            <ArrowRight
              size={14}
            />

          </button>

        </div>

      </section>


      <section className="pl-logistics-strip">

        <div>

          <Truck
            size={17}
          />

          <span>
            Total Orders
          </span>

          <strong>
            {
              formatNumber(
                summary.total_orders
              )
            }
          </strong>

        </div>


        <div>

          <PackageCheck
            size={17}
          />

          <span>
            Delivered
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .delivered_orders
              )
            }
          </strong>

        </div>


        <div>

          <Clock3
            size={17}
          />

          <span>
            Avg Delivery TAT
          </span>

          <strong>
            {
              summary
                .average_delivery_tat_days
                .toFixed(2)
            } days
          </strong>

        </div>


        <div>

          <WalletCards
            size={17}
          />

          <span>
            COD Share
          </span>

          <strong>
            {
              summary
                .cod_share_percent
                .toFixed(2)
            }%
          </strong>

        </div>

      </section>


      <section>

        <div className="pl-section-header">

          <div>

            <h2>
              Logistics health
            </h2>

            <p>
              Core delivery and exception
              metrics for the selected period.
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


      <section className="pl-logistics-analysis-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Payment risk
              </span>

              <h2>
                COD vs Prepaid
              </h2>

            </div>

          </div>


          <div className="pl-payment-risk-grid">

            {
              paymentGroups.map(
                row => (
                  <div
                    key={
                      row.payment_group
                    }
                    className="pl-payment-risk-card"
                  >

                    <strong>
                      {
                        row.payment_group
                      }
                    </strong>


                    <div>

                      <span>
                        Orders
                      </span>

                      <strong>
                        {
                          formatNumber(
                            row.orders
                          )
                        }
                      </strong>

                    </div>


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
                        NDR
                      </span>

                      <strong>
                        {
                          row
                            .ndr_rate_percent
                            .toFixed(2)
                        }%
                      </strong>

                    </div>


                    <div>

                      <span>
                        TAT
                      </span>

                      <strong>
                        {
                          row
                            .average_delivery_tat_days
                            .toFixed(2)
                        }d
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
                Speed leaders
              </span>

              <h2>
                Fastest couriers
              </h2>

            </div>

          </div>


          <div className="pl-courier-list">

            {
              fastestCouriers.map(
                row => (
                  <div
                    key={
                      row.courier_name
                    }
                    className="pl-courier-row"
                  >

                    <strong>
                      {
                        row.courier_name
                      }
                    </strong>


                    <div>

                      <span>
                        Avg TAT
                      </span>

                      <strong>
                        {
                          row
                            .average_delivery_tat_days
                            .toFixed(2)
                        }d
                      </strong>

                    </div>


                    <div>

                      <span>
                        Delivery
                      </span>

                      <strong>
                        {
                          row
                            .delivery_rate_percent
                            .toFixed(2)
                        }%
                      </strong>

                    </div>


                    <div>

                      <span>
                        On time
                      </span>

                      <strong>
                        {
                          row
                            .on_time_delivery_percent
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


      <section className="pl-logistics-analysis-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Courier risk
              </span>

              <h2>
                Highest RTO couriers
              </h2>

            </div>

          </div>


          <div className="pl-courier-list">

            {
              courierRisk.map(
                row => (
                  <div
                    key={
                      row.courier_name
                    }
                    className="pl-courier-row risk"
                  >

                    <strong>
                      {
                        row.courier_name
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
                        NDR
                      </span>

                      <strong>
                        {
                          row
                            .ndr_rate_percent
                            .toFixed(2)
                        }%
                      </strong>

                    </div>


                    <div>

                      <span>
                        Orders
                      </span>

                      <strong>
                        {
                          formatNumber(
                            row.orders
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


        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Geographic risk
              </span>

              <h2>
                Zone performance
              </h2>

            </div>

          </div>


          <div className="pl-zone-list">

            {
              zoneRisk.map(
                row => (
                  <div
                    key={
                      row.zone
                    }
                    className="pl-zone-row"
                  >

                    <strong>
                      {
                        row.zone
                      }
                    </strong>


                    <div>

                      <span>
                        Orders
                      </span>

                      <strong>
                        {
                          formatNumber(
                            row.orders
                          )
                        }
                      </strong>

                    </div>


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
                        NDR
                      </span>

                      <strong>
                        {
                          row
                            .ndr_rate_percent
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


      <section className="pl-founder-panel">

        <div className="pl-panel-header">

          <div>

            <span className="pl-page-eyebrow">
              Detailed carrier economics
            </span>

            <h2>
              Courier comparison
            </h2>

          </div>

        </div>


        <div className="table-wrap">

          <table className="data-table">

            <thead>

              <tr>
                <th>Courier</th>
                <th>Orders</th>
                <th>Delivery</th>
                <th>RTO</th>
                <th>NDR</th>
                <th>Avg TAT</th>
                <th>P90 TAT</th>
                <th>On Time</th>
                <th>Base Cost</th>
                <th>RTO Fee</th>
              </tr>

            </thead>


            <tbody>

              {
                couriers.map(
                  row => (
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
                        }d
                      </td>

                      <td>
                        {
                          row
                            .p90_delivery_tat_days
                            .toFixed(2)
                        }d
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
                            row
                              .base_shipping_cost
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

      </section>


      <section className="pl-logistics-scope-note">

        <RotateCcw
          size={20}
        />

        <div>

          <strong>
            Logistics metric scope
          </strong>

          <p>
            Delivery rate is based on recorded
            delivery timestamps. On-time delivery
            is calculated only for delivered orders
            with measurable promised dates.
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

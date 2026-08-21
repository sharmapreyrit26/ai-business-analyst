import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  PackageCheck,
  Timer,
  Truck,
} from 'lucide-react'

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  api,
} from '../api/profitlens'

import {
  ErrorState,
  LoadingState,
} from '../components/PageState'

import {
  SectionTitle,
} from '../components/SectionTitle'

import type {
  LogisticsAnalyticsResponse,
} from '../types/api'

import {
  fmtNumber,
  fmtPct,
} from '../utils'


type LogisticsProps = {
  month: string
}


export default function Logistics({
  month,
}: LogisticsProps) {
  const [
    data,
    setData,
  ] = useState<
    LogisticsAnalyticsResponse | null
  >(null)

  const [
    error,
    setError,
  ] = useState('')


  useEffect(() => {
    let active = true

    setData(null)
    setError('')

    api.logistics(
      month
    )
      .then((result) => {
        if (active) {
          setData(
            result
          )
        }
      })
      .catch((err) => {
        if (!active) {
          return
        }

        if (
          err instanceof Error
        ) {
          setError(
            err.message
          )
        } else {
          setError(
            'Unable to load logistics analytics.'
          )
        }
      })

    return () => {
      active = false
    }

  }, [month])


  const tatChartData =
    useMemo(() => {
      if (!data) {
        return []
      }

      const fulfilment =
        data.fulfilment_tat || {}

      const stages = [
        {
          name:
            'Purchase → Approval',

          data:
            fulfilment
              .purchase_to_approval,
        },
        {
          name:
            'Approval → Carrier',

          data:
            fulfilment
              .approval_to_carrier,
        },
        {
          name:
            'Carrier → Delivery',

          data:
            fulfilment
              .carrier_to_delivery,
        },
        {
          name:
            'Purchase → Delivery',

          data:
            fulfilment
              .purchase_to_delivery,
        },
      ]

      return stages
        .filter(
          (stage) =>
            stage.data
        )
        .map(
          (stage) => ({
            name:
              stage.name,

            average:
              Number(
                stage.data?.average
                || 0
              ),

            p90:
              Number(
                stage.data?.p90
                || 0
              ),
          })
        )

    }, [data])


  if (error) {
    return (
      <ErrorState
        error={error}
      />
    )
  }


  if (!data) {
    return (
      <LoadingState />
    )
  }


  const fulfilment =
    data.fulfilment_tat || {}


  const purchaseToDelivery =
    fulfilment
      .purchase_to_delivery
      || {}


  const approvalToCarrier =
    fulfilment
      .approval_to_carrier
      || {}


  const carrierToDelivery =
    fulfilment
      .carrier_to_delivery
      || {}


  const deliveryPromise =
    data.delivery_promise
    || {}


  const orderStatus =
    data.order_status
    || {}


  const dataQuality =
    data.data_quality
    || {}


  const avgDelivery =
    purchaseToDelivery
      .average


  const p90Delivery =
    purchaseToDelivery
      .p90


  const onTime =
    deliveryPromise
      .on_time_delivery_percent


  const late =
    deliveryPromise
      .late_delivery_percent


  return (
    <div className="page">

      <SectionTitle
        title="Logistics Analysis"
        subtitle={
          `Fulfilment and delivery performance for ${month}. `
          + 'All TAT and SLA metrics are calculated from order timestamps.'
        }
      />


      <div className="logistics-kpi-grid">

        <div className="card logistics-kpi">

          <div className="logistics-kpi-icon blue">
            <Clock3
              size={18}
            />
          </div>

          <div>
            <span>
              Avg Delivery TAT
            </span>

            <strong>
              {
                avgDelivery !== undefined
                  && avgDelivery !== null
                  ? `${avgDelivery.toFixed(2)} days`
                  : 'N/A'
              }
            </strong>

            <small>
              Purchase to customer delivery
            </small>
          </div>

        </div>


        <div className="card logistics-kpi">

          <div className="logistics-kpi-icon purple">
            <Timer
              size={18}
            />
          </div>

          <div>
            <span>
              P90 Delivery TAT
            </span>

            <strong>
              {
                p90Delivery !== undefined
                  && p90Delivery !== null
                  ? `${p90Delivery.toFixed(2)} days`
                  : 'N/A'
              }
            </strong>

            <small>
              90% of orders delivered within this TAT
            </small>
          </div>

        </div>


        <div className="card logistics-kpi">

          <div className="logistics-kpi-icon green">
            <CheckCircle2
              size={18}
            />
          </div>

          <div>
            <span>
              On-Time Delivery
            </span>

            <strong>
              {fmtPct(
                onTime
              )}
            </strong>

            <small>
              Delivered within promised date
            </small>
          </div>

        </div>


        <div className="card logistics-kpi">

          <div className="logistics-kpi-icon red">
            <AlertTriangle
              size={18}
            />
          </div>

          <div>
            <span>
              Late Delivery
            </span>

            <strong>
              {fmtPct(
                late
              )}
            </strong>

            <small>
              Delivered after promised date
            </small>
          </div>

        </div>

      </div>


      <div className="two-col">

        <div className="card chart-card">

          <div className="logistics-card-header">

            <div>

              <div className="card-title">
                Fulfilment TAT Breakdown
              </div>

              <p>
                Average versus P90 turnaround time
                across major fulfilment stages.
              </p>

            </div>

            <span className="badge blue">
              Days
            </span>

          </div>


          <ResponsiveContainer
            width="100%"
            height={340}
          >

            <BarChart
              data={tatChartData}
              layout="vertical"
            >

              <CartesianGrid
                stroke="#1E3A5F"
                horizontal={false}
              />


              <XAxis
                type="number"
                stroke="#64748B"
                tick={{
                  fontSize: 11,
                }}
              />


              <YAxis
                type="category"
                dataKey="name"
                stroke="#64748B"
                width={135}
                tick={{
                  fontSize: 10,
                }}
              />


              <Tooltip
                contentStyle={{
                  background:
                    '#162843',
                  border:
                    '1px solid #1E3A5F',
                  borderRadius: 10,
                }}
                formatter={(
                  value
                ) =>
                  `${Number(
                    value
                  ).toFixed(2)} days`
                }
              />


              <Bar
                dataKey="average"
                fill="#3B82F6"
                radius={[
                  0,
                  5,
                  5,
                  0,
                ]}
              />


              <Bar
                dataKey="p90"
                fill="#8B5CF6"
                radius={[
                  0,
                  5,
                  5,
                  0,
                ]}
              />

            </BarChart>

          </ResponsiveContainer>

        </div>


        <div className="card">

          <div className="card-title">
            Fulfilment Snapshot
          </div>


          <div className="metric-list">

            <div>
              <span>
                Approval → Carrier Avg
              </span>

              <strong>
                {
                  approvalToCarrier
                    .average !== undefined
                    && approvalToCarrier
                      .average !== null
                    ? `${
                      approvalToCarrier
                        .average
                        .toFixed(2)
                    } days`
                    : 'N/A'
                }
              </strong>
            </div>


            <div>
              <span>
                Carrier → Delivery Avg
              </span>

              <strong>
                {
                  carrierToDelivery
                    .average !== undefined
                    && carrierToDelivery
                      .average !== null
                    ? `${
                      carrierToDelivery
                        .average
                        .toFixed(2)
                    } days`
                    : 'N/A'
                }
              </strong>
            </div>


            <div>
              <span>
                Delivered Orders
              </span>

              <strong>
                {fmtNumber(
                  orderStatus
                    .delivered_orders
                )}
              </strong>
            </div>


            <div>
              <span>
                Cancelled Orders
              </span>

              <strong>
                {fmtNumber(
                  orderStatus
                    .cancelled_orders
                )}
              </strong>
            </div>


            <div>
              <span>
                Data Quality
              </span>

              <strong>
                {
                  String(
                    dataQuality
                      .status
                    || 'available'
                  )
                }
              </strong>
            </div>

          </div>


          <div className="notice info">
            This view separates average TAT from P90.
            P90 is usually more useful operationally because
            it highlights the slower tail of fulfilment
            performance.
          </div>

        </div>

      </div>


      <div className="card">

        <div className="logistics-card-header">

          <div>

            <div className="card-title">
              Delivery Promise Performance
            </div>

            <p>
              Comparison of orders delivered within
              versus after the promised customer date.
            </p>

          </div>

          <Truck
            size={18}
          />

        </div>


        <div className="delivery-promise-grid">

          <div className="delivery-promise-item good">

            <PackageCheck
              size={18}
            />

            <div>
              <span>
                On Time
              </span>

              <strong>
                {fmtPct(
                  onTime
                )}
              </strong>
            </div>

          </div>


          <div className="delivery-promise-item bad">

            <AlertTriangle
              size={18}
            />

            <div>
              <span>
                Late
              </span>

              <strong>
                {fmtPct(
                  late
                )}
              </strong>
            </div>

          </div>

        </div>

      </div>


      <div className="notice warning">
        Courier-level performance, RTO, NDR and COD vs
        prepaid analysis are intentionally unavailable
        until courier, return-status and payment-method
        data are connected.
      </div>

    </div>
  )
}
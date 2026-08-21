import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  Boxes,
  IndianRupee,
  PackageCheck,
  ReceiptIndianRupee,
  ShoppingCart,
  Truck,
} from 'lucide-react'

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { api } from '../api/profitlens'
import { ErrorState, LoadingState } from '../components/PageState'
import { KpiCard } from '../components/KpiCard'
import { SectionTitle } from '../components/SectionTitle'
import type { DashboardResponse } from '../types/api'
import {
  fmtMoney,
  fmtNumber,
  fmtPct,
  humanizeMetric,
} from '../utils'

type OverviewProps = {
  month: string
}

export default function Overview({
  month,
}: OverviewProps) {
  const [data, setData] =
    useState<DashboardResponse | null>(null)

  const [error, setError] =
    useState('')

  useEffect(() => {
    let active = true

    setData(null)
    setError('')

    api.dashboard(month)
      .then((result) => {
        if (active) {
          setData(result)
        }
      })
      .catch((err) => {
        if (!active) return

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load the ProfitLens dashboard.'
        )
      })

    return () => {
      active = false
    }
  }, [month])

  const chartData = useMemo(() => {
    if (!data) return []

    return data.monthly_revenue
      .map((row) => ({
        month: String(row.month || ''),
        revenue: Number(row.revenue || 0),
        orders: Number(row.orders || 0),
      }))
  }, [data])

  if (error) return <ErrorState error={error} />
  if (!data) return <LoadingState />

  const kpi = data.kpis

  const dataQuality = String(
    kpi.data_quality?.status || 'available'
  )

  const revenueGrowth =
    kpi.revenue.growth_percent

  const orderGrowth =
    kpi.orders.growth_percent

  const deliveryRate =
    kpi.delivery.rate_percent

  const cancellationRate =
    kpi.cancellation.rate_percent

  const businessStatus =
    (
      (revenueGrowth ?? 0) < 0
      || (orderGrowth ?? 0) < 0
    )
      ? 'Needs attention'
      : 'Healthy'

  return (
    <div className="page">
      <SectionTitle
        title="Business Overview"
        subtitle={
          `Management snapshot for ${month}. `
          + 'Every displayed metric is calculated by the ProfitLens backend.'
        }
      />

      <div className="overview-status-row">
        <div
          className={
            `overview-health ${
              businessStatus === 'Healthy'
                ? 'healthy'
                : 'attention'
            }`
          }
        >
          <div className="overview-health-icon">
            {
              businessStatus === 'Healthy'
                ? <PackageCheck size={18} />
                : <AlertTriangle size={18} />
            }
          </div>

          <div>
            <span>Business status</span>
            <strong>{businessStatus}</strong>
          </div>
        </div>

        <div className="overview-period">
          <span>Reporting period</span>
          <strong>{month}</strong>
        </div>

        <div className="overview-period">
          <span>Data quality</span>
          <strong>
            {humanizeMetric(dataQuality)}
          </strong>
        </div>
      </div>

      <div className="kpi-grid">
        <KpiCard
          label="Revenue"
          value={fmtMoney(kpi.revenue.value)}
          change={kpi.revenue.growth_percent}
          note="vs previous month"
          icon={<IndianRupee size={17} />}
        />

        <KpiCard
          label="Orders"
          value={fmtNumber(kpi.orders.value)}
          change={kpi.orders.growth_percent}
          note="vs previous month"
          icon={<ShoppingCart size={17} />}
        />

        <KpiCard
          label="Average Order Value"
          value={fmtMoney(kpi.aov.value)}
          change={kpi.aov.growth_percent}
          note="vs previous month"
          icon={<ReceiptIndianRupee size={17} />}
        />

        <KpiCard
          label="Delivery Rate"
          value={fmtPct(deliveryRate)}
          note={
            `${fmtNumber(
              kpi.delivery.delivered_orders
            )} delivered`
          }
          icon={<PackageCheck size={17} />}
        />
      </div>

      <div className="overview-secondary-grid">
        <div className="card overview-mini-card">
          <div className="overview-mini-icon red">
            <AlertTriangle size={16} />
          </div>

          <div>
            <span>Cancellation Rate</span>
            <strong>{fmtPct(cancellationRate)}</strong>
            <small>
              {fmtNumber(
                kpi.cancellation.cancelled_orders
              )} cancelled orders
            </small>
          </div>
        </div>

        <div className="card overview-mini-card">
          <div className="overview-mini-icon blue">
            <Truck size={16} />
          </div>

          <div>
            <span>Freight Value</span>
            <strong>
              {fmtMoney(kpi.freight.value)}
            </strong>
            <small>Total freight in period</small>
          </div>
        </div>

        <div className="card overview-mini-card">
          <div className="overview-mini-icon green">
            <Boxes size={16} />
          </div>

          <div>
            <span>Items Sold</span>
            <strong>
              {fmtNumber(kpi.items.value)}
            </strong>
            <small>Item-level volume</small>
          </div>
        </div>

        <div className="card overview-mini-card">
          <div className="overview-mini-icon amber">
            <ShoppingCart size={16} />
          </div>

          <div>
            <span>Delivered Orders</span>
            <strong>
              {fmtNumber(
                kpi.delivery.delivered_orders
              )}
            </strong>
            <small>Successfully delivered</small>
          </div>
        </div>
      </div>

      <div className="two-col">
        <div className="card chart-card">
          <div className="overview-card-header">
            <div>
              <div className="card-title">
                Monthly Revenue Trend
              </div>

              <p>
                Historical revenue movement across
                available reporting periods.
              </p>
            </div>

            <span className="badge blue">
              Revenue
            </span>
          </div>

          <ResponsiveContainer
            width="100%"
            height={320}
          >
            <AreaChart data={chartData}>
              <CartesianGrid
                stroke="#1E3A5F"
                vertical={false}
              />

              <XAxis
                dataKey="month"
                stroke="#64748B"
                tick={{ fontSize: 11 }}
              />

              <YAxis
                stroke="#64748B"
                tick={{ fontSize: 11 }}
                tickFormatter={(value) =>
                  `${Math.round(
                    value / 1000
                  )}k`
                }
              />

              <Tooltip
                contentStyle={{
                  background: '#162843',
                  border: '1px solid #1E3A5F',
                  borderRadius: 10,
                }}
                formatter={(value) =>
                  fmtMoney(Number(value))
                }
              />

              <Area
                type="monotone"
                dataKey="revenue"
                stroke="#3B82F6"
                fill="#3B82F622"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">
            Management Snapshot
          </div>

          <div className="metric-list">
            <div>
              <span>Revenue growth</span>
              <strong
                className={
                  (revenueGrowth ?? 0) >= 0
                    ? 'positive-text'
                    : 'negative-text'
                }
              >
                {fmtPct(revenueGrowth)}
              </strong>
            </div>

            <div>
              <span>Order growth</span>
              <strong
                className={
                  (orderGrowth ?? 0) >= 0
                    ? 'positive-text'
                    : 'negative-text'
                }
              >
                {fmtPct(orderGrowth)}
              </strong>
            </div>

            <div>
              <span>Delivery rate</span>
              <strong>
                {fmtPct(deliveryRate)}
              </strong>
            </div>

            <div>
              <span>Cancellation rate</span>
              <strong>
                {fmtPct(cancellationRate)}
              </strong>
            </div>

            <div>
              <span>Data quality</span>
              <strong>
                {humanizeMetric(dataQuality)}
              </strong>
            </div>
          </div>

          <div className="notice info">
            Profit, contribution margin, CAC, ROAS,
            RTO and customer LTV are intentionally
            excluded until the required cost,
            marketing, payment and logistics datasets
            are connected.
          </div>
        </div>
      </div>
    </div>
  )
}

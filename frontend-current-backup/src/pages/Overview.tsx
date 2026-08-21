import { useEffect, useMemo, useState } from 'react'
import { IndianRupee, PackageCheck, ReceiptIndianRupee, ShoppingCart } from 'lucide-react'
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
import { KpiCard } from '../components/KpiCard'
import { ErrorState, LoadingState } from '../components/PageState'
import { SectionTitle } from '../components/SectionTitle'
import type { DashboardResponse } from '../types/api'
import { fmtMoney, fmtNumber, fmtPct, humanizeMetric } from '../utils'

export default function Overview({ month }: { month: string }) {
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setData(null)
    setError('')

    api.dashboard(month)
      .then((result) => active && setData(result))
      .catch((err) => active && setError(err instanceof Error ? err.message : 'Unable to load dashboard.'))

    return () => { active = false }
  }, [month])

  const chartData = useMemo(
    () =>
      (data?.monthly_revenue || []).map((row) => ({
        month: String(row.month || ''),
        revenue: Number(row.revenue || 0),
      })),
    [data],
  )

  if (error) return <ErrorState error={error} />
  if (!data) return <LoadingState />

  const kpi = data.kpis

  return (
    <div className="page">
      <SectionTitle
        title="Business Overview"
        subtitle={`Management snapshot for ${month}. Metrics are calculated by the ProfitLens backend.`}
      />

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
          value={fmtPct(kpi.delivery.rate_percent)}
          note={`${fmtNumber(kpi.delivery.delivered_orders)} delivered`}
          icon={<PackageCheck size={17} />}
        />
      </div>

      <div className="two-col">
        <div className="card chart-card">
          <div className="card-title">Monthly Revenue Trend</div>
          <ResponsiveContainer width="100%" height={320}>
            <AreaChart data={chartData}>
              <CartesianGrid stroke="#1e3a5f" vertical={false} />
              <XAxis dataKey="month" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis
                stroke="#64748b"
                tick={{ fontSize: 11 }}
                tickFormatter={(value) => `${Math.round(Number(value) / 1000)}k`}
              />
              <Tooltip
                contentStyle={{
                  background: '#162843',
                  border: '1px solid #1e3a5f',
                  borderRadius: 10,
                }}
                formatter={(value) => fmtMoney(Number(value))}
              />
              <Area
                type="monotone"
                dataKey="revenue"
                stroke="#3b82f6"
                fill="#3b82f622"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">Management Snapshot</div>
          <div className="metric-list">
            <div><span>Revenue growth</span><strong>{fmtPct(kpi.revenue.growth_percent)}</strong></div>
            <div><span>Order growth</span><strong>{fmtPct(kpi.orders.growth_percent)}</strong></div>
            <div><span>Delivery rate</span><strong>{fmtPct(kpi.delivery.rate_percent)}</strong></div>
            <div><span>Cancellation rate</span><strong>{fmtPct(kpi.cancellation.rate_percent)}</strong></div>
            <div><span>Data quality</span><strong>{humanizeMetric(kpi.data_quality?.status)}</strong></div>
          </div>

          <div className="notice info">
            Profit, contribution margin, CAC, ROAS, RTO and LTV remain unavailable
            until the required datasets are connected.
          </div>
        </div>
      </div>
    </div>
  )
}

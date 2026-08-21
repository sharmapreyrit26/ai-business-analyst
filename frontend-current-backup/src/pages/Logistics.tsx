import { useEffect, useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from '../api/profitlens'
import { ErrorState, LoadingState } from '../components/PageState'
import { SectionTitle } from '../components/SectionTitle'
import type { LogisticsAnalyticsResponse } from '../types/api'
import { fmtNumber, fmtPct } from '../utils'

export default function Logistics({ month }: { month: string }) {
  const [data, setData] = useState<LogisticsAnalyticsResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setData(null)
    setError('')
    api.logistics(month)
      .then((result) => active && setData(result))
      .catch((err) => active && setError(err instanceof Error ? err.message : 'Unable to load logistics analytics.'))
    return () => { active = false }
  }, [month])

  const chartData = useMemo(() => {
    if (!data) return []
    const f = data.fulfilment_tat
    return [
      ['Purchase → Approval', f.purchase_to_approval],
      ['Approval → Carrier', f.approval_to_carrier],
      ['Carrier → Delivery', f.carrier_to_delivery],
      ['Purchase → Delivery', f.purchase_to_delivery],
    ]
      .filter(([, metric]) => metric)
      .map(([name, metric]) => ({
        name,
        average: Number((metric as { average?: number }).average || 0),
        p90: Number((metric as { p90?: number }).p90 || 0),
      }))
  }, [data])

  if (error) return <ErrorState error={error} />
  if (!data) return <LoadingState />

  const f = data.fulfilment_tat
  const p = data.delivery_promise as Record<string, unknown>
  const s = data.order_status as Record<string, unknown>

  return (
    <div className="page">
      <SectionTitle
        title="Logistics Analysis"
        subtitle={`Fulfilment and delivery performance for ${month}.`}
      />

      <div className="kpi-grid">
        <div className="card stat-card"><span>Avg Delivery TAT</span><strong>{f.purchase_to_delivery?.average?.toFixed(2) || '—'} days</strong></div>
        <div className="card stat-card"><span>P90 Delivery TAT</span><strong>{f.purchase_to_delivery?.p90?.toFixed(2) || '—'} days</strong></div>
        <div className="card stat-card"><span>On-Time Delivery</span><strong>{fmtPct(Number(p.on_time_delivery_percent || 0))}</strong></div>
        <div className="card stat-card"><span>Late Delivery</span><strong>{fmtPct(Number(p.late_delivery_percent || 0))}</strong></div>
      </div>

      <div className="two-col">
        <div className="card chart-card">
          <div className="card-title">Fulfilment TAT Breakdown</div>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={chartData} layout="vertical">
              <CartesianGrid stroke="#1e3a5f" horizontal={false} />
              <XAxis type="number" stroke="#64748b" />
              <YAxis type="category" dataKey="name" stroke="#64748b" width={130} tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  background: '#162843',
                  border: '1px solid #1e3a5f',
                  borderRadius: 10,
                }}
              />
              <Bar dataKey="average" fill="#3b82f6" />
              <Bar dataKey="p90" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">Fulfilment Snapshot</div>
          <div className="metric-list">
            <div><span>Delivered orders</span><strong>{fmtNumber(Number(s.delivered_orders || 0))}</strong></div>
            <div><span>Cancelled orders</span><strong>{fmtNumber(Number(s.cancelled_orders || 0))}</strong></div>
            <div><span>Approval → Carrier Avg</span><strong>{f.approval_to_carrier?.average?.toFixed(2) || '—'} days</strong></div>
            <div><span>Carrier → Delivery Avg</span><strong>{f.carrier_to_delivery?.average?.toFixed(2) || '—'} days</strong></div>
          </div>
        </div>
      </div>
    </div>
  )
}

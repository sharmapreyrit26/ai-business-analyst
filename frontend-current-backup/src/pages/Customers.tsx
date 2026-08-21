import { useEffect, useState } from 'react'
import { api } from '../api/profitlens'
import { ErrorState, LoadingState } from '../components/PageState'
import { SectionTitle } from '../components/SectionTitle'
import type { CustomerAnalyticsResponse } from '../types/api'
import { fmtNumber, fmtPct, humanizeMetric } from '../utils'

export default function Customers({ month }: { month: string }) {
  const [data, setData] = useState<CustomerAnalyticsResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setData(null)
    setError('')
    api.customers()
      .then((result) => active && setData(result))
      .catch((err) => active && setError(err instanceof Error ? err.message : 'Unable to load customer analytics.'))
    return () => { active = false }
  }, [month])

  if (error) return <ErrorState error={error} />
  if (!data) return <LoadingState />

  const q = data.data_quality as Record<string, unknown>
  const available = data.available_analysis as Record<string, unknown>
  const summary = (available.customer_order_summary || {}) as Record<string, unknown>
  const next = data.next_data_requirement as Record<string, unknown>

  return (
    <div className="page">
      <SectionTitle
        title="Customer Analysis"
        subtitle="Available customer-data coverage and what is still required for retention, repeat purchase and LTV."
      />

      <div className="notice warning">
        Customer analytics status: <strong>{humanizeMetric(data.status)}</strong>. ProfitLens will not fabricate retention metrics without persistent customer identity.
      </div>

      <div className="kpi-grid">
        <div className="card stat-card"><span>Customer Records</span><strong>{fmtNumber(Number(q.total_orders || 0))}</strong></div>
        <div className="card stat-card"><span>Unique Customer IDs</span><strong>{fmtNumber(Number(q.unique_customer_ids || 0))}</strong></div>
        <div className="card stat-card"><span>ID Coverage</span><strong>{fmtPct(Number(q.customer_id_coverage_percent || 0))}</strong></div>
        <div className="card stat-card"><span>Persistent ID</span><strong>{q.persistent_customer_identifier_available ? 'Available' : 'Missing'}</strong></div>
      </div>

      <div className="two-col">
        <div className="card">
          <div className="card-title">Available Analysis</div>
          <div className="metric-list">
            <div><span>Customer records</span><strong>{fmtNumber(Number(summary.customer_records || 0))}</strong></div>
            <div><span>Avg orders per customer ID</span><strong>{String(summary.average_orders_per_customer_id ?? 'N/A')}</strong></div>
            <div><span>Max orders for one customer ID</span><strong>{fmtNumber(Number(summary.maximum_orders_for_single_customer_id || 0))}</strong></div>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Next Data Requirement</div>
          <div className="metric-list">
            <div><span>Dataset</span><strong>{String(next.dataset || 'Customer master data')}</strong></div>
            <div><span>Critical field</span><strong className="mono">{String(next.critical_field || 'customer_unique_id')}</strong></div>
          </div>
          <div className="notice info">{String(next.reason || 'Persistent customer identity is required.')}</div>
        </div>
      </div>
    </div>
  )
}

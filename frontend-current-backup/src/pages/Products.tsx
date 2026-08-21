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
import type { ProductAnalyticsResponse } from '../types/api'
import { fmtMoney, fmtNumber, fmtPct } from '../utils'

export default function Products({ month }: { month: string }) {
  const [data, setData] = useState<ProductAnalyticsResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setData(null)
    setError('')
    api.products(month)
      .then((result) => active && setData(result))
      .catch((err) => active && setError(err instanceof Error ? err.message : 'Unable to load product analytics.'))
    return () => { active = false }
  }, [month])

  const chartData = useMemo(
    () =>
      (data?.top_products || []).slice(0, 10).map((product, index) => ({
        name: `#${index + 1}`,
        revenue: Number(product.revenue || 0),
      })),
    [data],
  )

  if (error) return <ErrorState error={error} />
  if (!data) return <LoadingState />

  return (
    <div className="page">
      <SectionTitle
        title="Product Analysis"
        subtitle={`Commercial product performance for ${month}. Profitability stays unavailable until cost data is connected.`}
      />

      <div className="kpi-grid">
        <div className="card stat-card"><span>Products Sold</span><strong>{fmtNumber(data.summary.total_products)}</strong></div>
        <div className="card stat-card"><span>Product Revenue</span><strong>{fmtMoney(data.summary.total_revenue)}</strong></div>
        <div className="card stat-card"><span>Units Sold</span><strong>{fmtNumber(data.summary.total_units)}</strong></div>
        <div className="card stat-card"><span>Top 10 Revenue Share</span><strong>{fmtPct(data.concentration.top_10_revenue_share_percent)}</strong></div>
      </div>

      <div className="card chart-card">
        <div className="card-title">Top Products by Revenue</div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid stroke="#1e3a5f" vertical={false} />
            <XAxis dataKey="name" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip
              contentStyle={{
                background: '#162843',
                border: '1px solid #1e3a5f',
                borderRadius: 10,
              }}
              formatter={(value) => fmtMoney(Number(value))}
            />
            <Bar dataKey="revenue" fill="#3b82f6" radius={[5, 5, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card table-card">
        <div className="card-title">Product Performance</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Product ID</th>
                <th>Revenue</th>
                <th>Units</th>
                <th>Orders</th>
                <th>Avg Price</th>
                <th>Revenue Share</th>
                <th>Freight / Revenue</th>
              </tr>
            </thead>
            <tbody>
              {data.top_products.map((product, index) => (
                <tr key={product.product_id || index}>
                  <td>#{index + 1}</td>
                  <td className="mono">{product.product_id?.slice(0, 14)}…</td>
                  <td>{fmtMoney(product.revenue)}</td>
                  <td>{fmtNumber(product.units_sold)}</td>
                  <td>{fmtNumber(product.orders)}</td>
                  <td>{fmtMoney(product.average_selling_price)}</td>
                  <td>{fmtPct(product.revenue_share_percent)}</td>
                  <td>{fmtPct(product.freight_to_revenue_percent)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

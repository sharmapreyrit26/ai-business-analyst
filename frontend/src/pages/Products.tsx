import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  Boxes,
  IndianRupee,
  Package,
  ReceiptIndianRupee,
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

import { api } from '../api/profitlens'
import { ErrorState, LoadingState } from '../components/PageState'
import { SectionTitle } from '../components/SectionTitle'
import type { ProductAnalyticsResponse } from '../types/api'
import {
  fmtMoney,
  fmtNumber,
  fmtPct,
} from '../utils'

type ProductsProps = {
  month: string
}

type ProductRow = {
  product_id?: string
  revenue?: number
  units_sold?: number
  orders?: number
  average_selling_price?: number
  revenue_share_percent?: number
  freight_value?: number
  freight_to_revenue_percent?: number
}

export default function Products({
  month,
}: ProductsProps) {
  const [data, setData] =
    useState<ProductAnalyticsResponse | null>(null)

  const [error, setError] =
    useState('')

  useEffect(() => {
    let active = true

    setData(null)
    setError('')

    api.products(month)
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
            : 'Unable to load product analytics.'
        )
      })

    return () => {
      active = false
    }
  }, [month])

  const rows =
    useMemo<ProductRow[]>(
      () => {
        if (!data) return []

        return (
          data.top_products
          || []
        ) as ProductRow[]
      },
      [data]
    )

  const chartData =
    useMemo(
      () => (
        rows
          .slice(0, 10)
          .map((product, index) => ({
            name: `#${index + 1}`,
            product_id: product.product_id,
            revenue: Number(
              product.revenue || 0
            ),
            share: Number(
              product.revenue_share_percent || 0
            ),
          }))
      ),
      [rows]
    )

  if (error) return <ErrorState error={error} />
  if (!data) return <LoadingState />

  const summary =
    data.summary || {}

  const concentration =
    data.concentration || {}

  const topProduct =
    rows[0]

  return (
    <div className="page">
      <SectionTitle
        title="Product Analysis"
        subtitle={
          `Product-level commercial performance for ${month}. `
          + 'Revenue is kept separate from profit until cost data is connected.'
        }
      />

      <div className="product-kpi-grid">
        <div className="card product-kpi">
          <div className="product-kpi-icon blue">
            <Package size={17} />
          </div>
          <div>
            <span>Products Sold</span>
            <strong>
              {fmtNumber(summary.total_products)}
            </strong>
            <small>Unique products in period</small>
          </div>
        </div>

        <div className="card product-kpi">
          <div className="product-kpi-icon green">
            <IndianRupee size={17} />
          </div>
          <div>
            <span>Product Revenue</span>
            <strong>
              {fmtMoney(summary.total_revenue)}
            </strong>
            <small>Total product sales value</small>
          </div>
        </div>

        <div className="card product-kpi">
          <div className="product-kpi-icon amber">
            <Boxes size={17} />
          </div>
          <div>
            <span>Units Sold</span>
            <strong>
              {fmtNumber(summary.total_units)}
            </strong>
            <small>Total item volume</small>
          </div>
        </div>

        <div className="card product-kpi">
          <div className="product-kpi-icon purple">
            <ReceiptIndianRupee size={17} />
          </div>
          <div>
            <span>Top 10 Revenue Share</span>
            <strong>
              {fmtPct(
                concentration.top_10_revenue_share_percent
              )}
            </strong>
            <small>Product concentration</small>
          </div>
        </div>
      </div>

      <div className="two-col">
        <div className="card chart-card">
          <div className="product-card-header">
            <div>
              <div className="card-title">
                Top Products by Revenue
              </div>
              <p>
                Revenue contribution of the highest
                performing products in the selected month.
              </p>
            </div>

            <span className="badge blue">
              Top 10
            </span>
          </div>

          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chartData}>
              <CartesianGrid
                stroke="#1E3A5F"
                vertical={false}
              />

              <XAxis
                dataKey="name"
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

              <Bar
                dataKey="revenue"
                fill="#3B82F6"
                radius={[5, 5, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">
            Product Snapshot
          </div>

          <div className="metric-list">
            <div>
              <span>Leading product</span>
              <strong className="mono">
                {
                  topProduct
                    ?.product_id
                    ?.slice(0, 12)
                  || 'N/A'
                }
              </strong>
            </div>

            <div>
              <span>Leading product revenue</span>
              <strong>
                {fmtMoney(topProduct?.revenue)}
              </strong>
            </div>

            <div>
              <span>Units sold</span>
              <strong>
                {fmtNumber(topProduct?.units_sold)}
              </strong>
            </div>

            <div>
              <span>Revenue contribution</span>
              <strong>
                {fmtPct(
                  topProduct?.revenue_share_percent
                )}
              </strong>
            </div>

            <div>
              <span>Freight / Revenue</span>
              <strong>
                {fmtPct(
                  topProduct?.freight_to_revenue_percent
                )}
              </strong>
            </div>
          </div>

          <div className="notice info">
            Revenue concentration can identify products
            that matter commercially, but it does not tell
            us which products are most profitable.
          </div>
        </div>
      </div>

      <div className="card table-card">
        <div className="product-card-header">
          <div>
            <div className="card-title">
              Product Performance Table
            </div>
            <p>
              Revenue, volume, pricing and freight burden
              for the highest-revenue products.
            </p>
          </div>

          <span className="badge blue">
            {rows.length} products
          </span>
        </div>

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
              {rows.map(
                (product, index) => (
                  <tr
                    key={
                      product.product_id
                      || index
                    }
                  >
                    <td>
                      <span className="product-rank">
                        #{index + 1}
                      </span>
                    </td>

                    <td
                      className="mono"
                      title={product.product_id}
                    >
                      {
                        product.product_id
                          ?.slice(0, 14)
                      }
                      …
                    </td>

                    <td>{fmtMoney(product.revenue)}</td>
                    <td>{fmtNumber(product.units_sold)}</td>
                    <td>{fmtNumber(product.orders)}</td>
                    <td>
                      {fmtMoney(
                        product.average_selling_price
                      )}
                    </td>
                    <td>
                      {fmtPct(
                        product.revenue_share_percent
                      )}
                    </td>
                    <td>
                      <div className="freight-cell">
                        <Truck size={13} />
                        {fmtPct(
                          product.freight_to_revenue_percent
                        )}
                      </div>
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="notice warning">
        Product profitability is intentionally unavailable.
        ProfitLens requires COGS and additional variable-cost
        data before calculating gross profit, contribution
        margin or true SKU profitability.
      </div>
    </div>
  )
}

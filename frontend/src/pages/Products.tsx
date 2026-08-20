import { useEffect, useState } from 'react'
import { api } from '../api/profitlens'
import { ErrorState, LoadingState } from '../components/PageState'
import { SectionTitle } from '../components/SectionTitle'
import type { ProductAnalyticsResponse } from '../types/api'
import { fmtMoney, fmtNumber, fmtPct } from '../utils'

export default function Products({ month }: { month: string }) {
  const [data,setData]=useState<ProductAnalyticsResponse|null>(null); const [error,setError]=useState('')
  useEffect(()=>{setData(null);setError('');api.products(month).then(setData).catch(e=>setError(e.message))},[month])
  if(error) return <ErrorState error={error}/>; if(!data) return <LoadingState/>
  const rows=data.top_products || []
  return <div className="page"><SectionTitle title="Product Analysis" subtitle="Revenue contribution, units, orders and freight burden by product."/>
    <div className="summary-strip"><div><span>Total products</span><strong>{fmtNumber(data.summary?.total_products)}</strong></div><div><span>Total revenue</span><strong>{fmtMoney(data.summary?.total_revenue)}</strong></div><div><span>Total units</span><strong>{fmtNumber(data.summary?.total_units)}</strong></div><div><span>Top 10 share</span><strong>{fmtPct(data.concentration?.top_10_revenue_share_percent)}</strong></div></div>
    <div className="card table-card"><div className="card-title">Top products by revenue</div><div className="table-wrap"><table><thead><tr><th>Product ID</th><th>Revenue</th><th>Units</th><th>Orders</th><th>Avg price</th><th>Revenue share</th><th>Freight / Revenue</th></tr></thead><tbody>{rows.map((r:any)=><tr key={r.product_id}><td className="mono">{r.product_id}</td><td>{fmtMoney(r.revenue)}</td><td>{fmtNumber(r.units_sold)}</td><td>{fmtNumber(r.orders)}</td><td>{fmtMoney(r.average_selling_price)}</td><td>{fmtPct(r.revenue_share_percent)}</td><td>{fmtPct(r.freight_to_revenue_percent)}</td></tr>)}</tbody></table></div></div>
    <div className="notice warning">Product profitability is unavailable until COGS and variable costs are connected. Revenue is not treated as profit.</div>
  </div>
}

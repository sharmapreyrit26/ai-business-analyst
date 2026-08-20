import { useEffect, useState } from 'react'
import { IndianRupee, PackageCheck, ReceiptIndianRupee, ShoppingCart } from 'lucide-react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api/profitlens'
import { ErrorState, LoadingState } from '../components/PageState'
import { KpiCard } from '../components/KpiCard'
import { SectionTitle } from '../components/SectionTitle'
import type { DashboardResponse } from '../types/api'
import { fmtMoney, fmtNumber, fmtPct } from '../utils'

export default function Overview({ month }: { month: string }) {
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [error, setError] = useState('')
  useEffect(() => { setData(null); setError(''); api.dashboard(month).then(setData).catch((e) => setError(e.message)) }, [month])
  if (error) return <ErrorState error={error}/>
  if (!data) return <LoadingState/>

  const k = data.kpis
  const chartData = data.monthly_revenue.filter((r) => r.month && r.month !== '2018-09').map((r) => ({ month: String(r.month), revenue: Number(r.revenue || 0), orders: Number(r.orders || 0) }))

  return <div className="page">
    <SectionTitle title="Business Overview" subtitle={`Performance snapshot for ${month}. All values come from the backend analytics engine.`}/>
    <div className="kpi-grid">
      <KpiCard label="Revenue" value={fmtMoney(k.revenue.value)} change={k.revenue.growth_percent} icon={<IndianRupee size={17}/>}/>
      <KpiCard label="Orders" value={fmtNumber(k.orders.value)} change={k.orders.growth_percent} icon={<ShoppingCart size={17}/>}/>
      <KpiCard label="AOV" value={fmtMoney(k.aov.value)} change={k.aov.growth_percent} icon={<ReceiptIndianRupee size={17}/>}/>
      <KpiCard label="Delivery Rate" value={fmtPct(k.delivery.rate_percent)} note={`${fmtNumber(k.delivery.delivered_orders)} delivered`} icon={<PackageCheck size={17}/>}/>
    </div>

    <div className="two-col">
      <div className="card chart-card">
        <div className="card-title">Monthly Revenue Trend</div>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}><defs><linearGradient id="rev" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3B82F6" stopOpacity={0.35}/><stop offset="100%" stopColor="#3B82F6" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#1E3A5F" vertical={false}/><XAxis dataKey="month" stroke="#64748B" tick={{fontSize:11}}/><YAxis stroke="#64748B" tick={{fontSize:11}} tickFormatter={(v) => `${Math.round(v/1000)}k`}/><Tooltip contentStyle={{background:'#162843',border:'1px solid #1E3A5F',borderRadius:10}} formatter={(v) => fmtMoney(Number(v))}/><Area type="monotone" dataKey="revenue" stroke="#3B82F6" fill="url(#rev)" strokeWidth={2}/></AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="card">
        <div className="card-title">Operational Health</div>
        <div className="metric-list">
          <div><span>Cancellation rate</span><strong>{fmtPct(k.cancellation.rate_percent)}</strong></div>
          <div><span>Freight value</span><strong>{fmtMoney(k.freight.value)}</strong></div>
          <div><span>Items sold</span><strong>{fmtNumber(k.items.value)}</strong></div>
          <div><span>Data quality</span><strong>{String(k.data_quality?.status || 'available')}</strong></div>
        </div>
        <div className="notice info">Profit, CAC, ROAS, RTO and contribution margin are intentionally not shown until the required cost/marketing/logistics datasets are connected.</div>
      </div>
    </div>
  </div>
}

import { useEffect, useState } from 'react'
import { api } from '../api/profitlens'
import { ErrorState, LoadingState } from '../components/PageState'
import { SectionTitle } from '../components/SectionTitle'
import type { CustomerAnalyticsResponse } from '../types/api'
import { fmtNumber, fmtPct } from '../utils'

export default function Customers(){
 const [data,setData]=useState<CustomerAnalyticsResponse|null>(null); const [error,setError]=useState('')
 useEffect(()=>{api.customers().then(setData).catch(e=>setError(e.message))},[])
 if(error)return <ErrorState error={error}/>; if(!data)return <LoadingState/>
 const dq:any=data.data_quality; const summary:any=data.available_analysis?.customer_order_summary
 return <div className="page"><SectionTitle title="Customer Analysis" subtitle="ProfitLens shows what is measurable and explicitly flags what cannot yet be calculated."/>
 <div className="kpi-grid compact"><div className="card mini"><span>Customer ID coverage</span><strong>{fmtPct(dq.customer_id_coverage_percent)}</strong></div><div className="card mini"><span>Customer records</span><strong>{fmtNumber(summary?.customer_records)}</strong></div><div className="card mini"><span>Avg orders / record</span><strong>{summary?.average_orders_per_customer_id ?? '—'}</strong></div><div className="card mini"><span>Data status</span><strong className="amber-text">{data.status}</strong></div></div>
 <div className="card"><div className="card-title">What we cannot calculate yet</div><div className="gap-list">{Object.entries(data.unavailable_analysis).map(([key,val]:any)=><div className="gap-row" key={key}><div><strong>{key.replaceAll('_',' ')}</strong><p>{val.reason}</p></div><span className="badge amber">{val.status}</span></div>)}</div></div>
 <div className="notice info"><strong>Next data requirement:</strong> {data.next_data_requirement?.dataset} • critical field: <span className="mono">{data.next_data_requirement?.critical_field}</span></div>
 </div>
}

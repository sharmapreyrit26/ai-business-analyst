import { useEffect, useState } from 'react'
import { api } from '../api/profitlens'
import { ErrorState, LoadingState } from '../components/PageState'
import { SectionTitle } from '../components/SectionTitle'
import type { LogisticsAnalyticsResponse } from '../types/api'
import { fmtNumber, fmtPct } from '../utils'

const tatLabel: Record<string,string>={purchase_to_approval:'Purchase → Approval',approval_to_carrier:'Approval → Carrier',carrier_to_delivery:'Carrier → Delivery',purchase_to_delivery:'Purchase → Delivery'}
export default function Logistics({month}:{month:string}){
 const [data,setData]=useState<LogisticsAnalyticsResponse|null>(null); const [error,setError]=useState('')
 useEffect(()=>{setData(null);api.logistics(month).then(setData).catch(e=>setError(e.message))},[month])
 if(error)return <ErrorState error={error}/>; if(!data)return <LoadingState/>
 const promise:any=data.delivery_promise
 return <div className="page"><SectionTitle title="Logistics & Fulfilment" subtitle="TAT distribution and promised-delivery performance based on actual order timestamps."/>
 <div className="kpi-grid compact"><div className="card mini"><span>On-time delivery</span><strong>{fmtPct(promise?.on_time_delivery_percent)}</strong></div><div className="card mini"><span>Late delivery</span><strong>{fmtPct(promise?.late_delivery_percent)}</strong></div><div className="card mini"><span>Measured orders</span><strong>{fmtNumber(promise?.measured_orders)}</strong></div><div className="card mini"><span>Avg days late</span><strong>{promise?.average_days_late ?? '—'}</strong></div></div>
 <div className="card table-card"><div className="card-title">Fulfilment TAT</div><table><thead><tr><th>Stage</th><th>Average</th><th>Median</th><th>P90</th><th>Sample</th></tr></thead><tbody>{Object.entries(data.fulfilment_tat||{}).filter(([k])=>k!=='month').map(([key,val]:any)=><tr key={key}><td>{tatLabel[key]||key}</td><td>{val.average ?? '—'} {val.unit}</td><td>{val.median ?? '—'} {val.unit}</td><td><strong>{val.p90 ?? '—'} {val.unit}</strong></td><td>{fmtNumber(val.sample_size)}</td></tr>)}</tbody></table></div>
 <div className="notice warning">Courier, RTO, NDR, COD/prepaid and first-attempt-delivery metrics remain disabled until those fields are connected.</div>
 </div>
}

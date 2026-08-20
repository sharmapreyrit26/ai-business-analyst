import { FormEvent, useState } from 'react'
import { Play } from 'lucide-react'
import { api } from '../api/profitlens'
import { SectionTitle } from '../components/SectionTitle'
import type { ScenarioResponse } from '../types/api'
import { fmtMoney } from '../utils'

export default function Scenario({month}:{month:string}){
 const [question,setQuestion]=useState('What if AOV increases by 12%?'); const [data,setData]=useState<ScenarioResponse|null>(null); const [loading,setLoading]=useState(false); const [error,setError]=useState('')
 async function submit(e:FormEvent){e.preventDefault();setLoading(true);setError('');try{setData(await api.scenario(question,month))}catch(err:any){setError(err.message)}finally{setLoading(false)}}
 const result:any=data?.scenario_result
 return <div className="page"><SectionTitle title="Scenario Lab" subtitle="Deterministic what-if analysis. Scenarios are calculations, not forecasts."/>
 <div className="card"><form onSubmit={submit} className="scenario-form"><input value={question} onChange={e=>setQuestion(e.target.value)}/><button className="primary-btn"><Play size={15}/>{loading?'Running…':'Run scenario'}</button></form></div>{error&&<div className="notice error">{error}</div>}
 {data&&<div className="scenario-grid"><div className="card"><div className="card-title">Scenario</div><div className="metric-list"><div><span>Type</span><strong>{data.scenario_type}</strong></div>{Object.entries(data.parameters||{}).map(([k,v])=><div key={k}><span>{k.replaceAll('_',' ')}</span><strong>{String(v)}</strong></div>)}</div></div><div className="card"><div className="card-title">Estimated impact</div>{result?.difference ? <div className="metric-list">{Object.entries(result.difference).map(([k,v]:any)=><div key={k}><span>{k.replaceAll('_',' ')}</span><strong>{k.includes('revenue')?fmtMoney(v):String(v)}</strong></div>)}</div>:<p className="muted">No impact result available.</p>}</div></div>}
 {result?.limitations?.length>0&&<div className="notice warning"><strong>Limitations</strong><ul>{result.limitations.map((x:string,i:number)=><li key={i}>{x}</li>)}</ul></div>}
 </div>
}

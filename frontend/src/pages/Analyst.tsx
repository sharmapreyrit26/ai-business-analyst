import { FormEvent, useState } from 'react'
import { Send } from 'lucide-react'
import { api } from '../api/profitlens'
import { SectionTitle } from '../components/SectionTitle'
import type { BusinessAnswerResponse } from '../types/api'

const suggestions=['Why did revenue decline?','Which products generated the most revenue?','What is our P90 delivery TAT?','What should management focus on?']
export default function Analyst({month}:{month:string}){
 const [question,setQuestion]=useState('Why did revenue decline?'); const [data,setData]=useState<BusinessAnswerResponse|null>(null); const [loading,setLoading]=useState(false); const [error,setError]=useState('')
 async function submit(e?:FormEvent){e?.preventDefault(); if(!question.trim())return; setLoading(true);setError('');try{setData(await api.ask(question,month))}catch(err:any){setError(err.message)}finally{setLoading(false)}}
 return <div className="page"><SectionTitle title="Ask ProfitLens" subtitle="Natural-language business questions routed to deterministic analytics before AI interpretation."/>
 <div className="analyst-layout"><div className="card"><form onSubmit={submit} className="ask-form"><textarea value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask a business question…"/><button className="primary-btn" disabled={loading}>{loading?'Analyzing…':<><Send size={15}/> Analyze</>}</button></form><div className="suggestions">{suggestions.map(s=><button key={s} onClick={()=>setQuestion(s)}>{s}</button>)}</div></div>
 {error&&<div className="notice error">{error}</div>}
 {data&&<div className="card answer-card"><div className="answer-meta"><span className="badge blue">{data.question_type}</span><span className={`badge ${data.ai_available?'green':'amber'}`}>{data.ai_available?'AI interpretation':'Deterministic fallback'}</span>{data.analysis_execution&&<span className="muted">{data.analysis_execution.successful_steps}/{data.analysis_execution.total_steps} analyses completed</span>}</div><h3>{data.answer.answer}</h3>{data.answer.likely_driver&&<div className="answer-block"><span>Likely driver</span><p>{data.answer.likely_driver}</p></div>}{data.answer.evidence?.length>0&&<div className="answer-block"><span>Evidence</span><ul>{data.answer.evidence.map((x,i)=><li key={i}>{x}</li>)}</ul></div>}{data.answer.recommended_actions?.length>0&&<div className="answer-block"><span>Recommended actions</span><ol>{data.answer.recommended_actions.map((x,i)=><li key={i}>{x}</li>)}</ol></div>}</div>}
 </div></div>
}

import { FormEvent, useState } from 'react'
import { Send } from 'lucide-react'
import { api } from '../api/profitlens'
import { SectionTitle } from '../components/SectionTitle'
import type { BusinessAnswerResponse } from '../types/api'
import { humanizeMetric } from '../utils'

const suggestions = [
  'Why did revenue decline?',
  'Which products generated the most revenue?',
  'What is our P90 delivery TAT?',
  'What should management focus on?',
]

export default function Analyst({ month }: { month: string }) {
  const [question, setQuestion] = useState('Why did revenue decline?')
  const [data, setData] = useState<BusinessAnswerResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit(event?: FormEvent) {
    event?.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    setError('')
    try {
      setData(await api.ask(question.trim(), month))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to analyze the question.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <SectionTitle
        title="Ask ProfitLens"
        subtitle={`AI-assisted analysis for ${month}. Business facts are calculated deterministically before AI interpretation.`}
      />

      <div className="analyst-layout">
        <div className="card">
          <form onSubmit={submit} className="ask-form">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a business question…"
              disabled={loading}
            />
            <button className="primary-btn" disabled={loading || !question.trim()}>
              {loading ? 'Analyzing…' : <><Send size={15} /> Analyze</>}
            </button>
          </form>

          <div className="suggestions">
            {suggestions.map((suggestion) => (
              <button key={suggestion} type="button" onClick={() => setQuestion(suggestion)}>
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {error && <div className="notice error">{error}</div>}

        {data && (
          <div className="card answer-card">
            <div className="answer-meta">
              <span className="badge blue">{humanizeMetric(data.question_type)}</span>
              <span className={`badge ${data.ai_available ? 'green' : 'amber'}`}>
                {data.ai_available ? 'AI interpretation' : 'Deterministic fallback'}
              </span>
            </div>

            <h3>{data.answer.answer}</h3>

            {data.answer.likely_driver && (
              <div className="answer-block">
                <span>Likely driver</span>
                <p>{humanizeMetric(data.answer.likely_driver)}</p>
              </div>
            )}

            {data.answer.evidence?.length > 0 && (
              <div className="answer-block">
                <span>Evidence</span>
                <ul>
                  {data.answer.evidence.map((item, index) => <li key={index}>{item}</li>)}
                </ul>
              </div>
            )}

            {data.answer.recommended_actions?.length > 0 && (
              <div className="answer-block">
                <span>Recommended actions</span>
                <ol>
                  {data.answer.recommended_actions.map((item, index) => <li key={index}>{item}</li>)}
                </ol>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

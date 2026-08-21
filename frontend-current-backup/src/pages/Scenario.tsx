import { FormEvent, useState } from 'react'
import { Calculator, Play } from 'lucide-react'
import { api } from '../api/profitlens'
import { SectionTitle } from '../components/SectionTitle'
import type { ScenarioResponse } from '../types/api'
import { fmtMoney, fmtNumber, humanizeMetric } from '../utils'

type ScenarioPayload = {
  assumptions?: Record<string, string | number | boolean | null>
  current?: { revenue?: number; orders?: number; aov?: number }
  scenario_result?: { revenue?: number; orders?: number; aov?: number }
  difference?: Record<string, number | null>
  limitations?: string[]
}

const presets = [
  'What if AOV increases by 5%?',
  'What if AOV increases by 12%?',
  'What happens if we recover half of lost orders?',
  'What if orders increase by 5% and AOV increases by 5%?',
]

export default function Scenario({ month }: { month: string }) {
  const [question, setQuestion] = useState('What if AOV increases by 12%?')
  const [data, setData] = useState<ScenarioResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit(event?: FormEvent) {
    event?.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    setError('')
    try {
      setData(await api.scenario(question.trim(), month))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to run scenario.')
    } finally {
      setLoading(false)
    }
  }

  const payload = data?.scenario_result as ScenarioPayload | null | undefined
  const current = payload?.current ?? {}
  const simulated = payload?.scenario_result ?? {}
  const difference = payload?.difference ?? {}
  const assumptions = payload?.assumptions ?? {}
  const limitations = payload?.limitations ?? []

  return (
    <div className="page">
      <SectionTitle
        title="Scenario Lab"
        subtitle={`Deterministic what-if analysis for ${month}. Scenarios are sensitivity calculations, not forecasts.`}
      />

      <div className="card">
        <form onSubmit={submit} className="scenario-form">
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="What if AOV increases by 10%?"
          />
          <button className="primary-btn" disabled={loading || !question.trim()}>
            <Play size={15} /> {loading ? 'Running…' : 'Run Scenario'}
          </button>
        </form>

        <div className="suggestions">
          {presets.map((preset) => (
            <button key={preset} type="button" onClick={() => setQuestion(preset)}>
              {preset}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="notice error">{error}</div>}

      {data && (
        <>
          <div className="kpi-grid">
            <div className="card stat-card"><span>Scenario Type</span><strong>{humanizeMetric(data.scenario_type || 'scenario')}</strong></div>
            <div className="card stat-card"><span>Status</span><strong>{humanizeMetric(data.status)}</strong></div>
            <div className="card stat-card"><span>Current Revenue</span><strong>{fmtMoney(current.revenue)}</strong></div>
            <div className="card stat-card"><span>Scenario Revenue</span><strong>{fmtMoney(simulated.revenue)}</strong></div>
          </div>

          <div className="two-col">
            <div className="card">
              <div className="card-title">Estimated Impact</div>
              <div className="metric-list">
                {Object.entries(difference).map(([key, value]) => (
                  <div key={key}>
                    <span>{humanizeMetric(key)}</span>
                    <strong>{key.includes('revenue') ? fmtMoney(value) : fmtNumber(value)}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="card-title">Assumptions</div>
              <div className="metric-list">
                {Object.entries(assumptions).map(([key, value]) => (
                  <div key={key}>
                    <span>{humanizeMetric(key)}</span>
                    <strong>{String(value)}</strong>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {limitations.length > 0 && (
            <div className="notice warning">
              <strong>Scenario limitations</strong>
              <ul>{limitations.map((item, index) => <li key={index}>{item}</li>)}</ul>
            </div>
          )}

          <div className="notice info">
            <Calculator size={15} /> ProfitLens scenario outputs show what would happen under explicit assumptions; they do not predict customer behavior.
          </div>
        </>
      )}
    </div>
  )
}

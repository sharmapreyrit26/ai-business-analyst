import {
  FormEvent,
  useState,
} from 'react'

import {
  BrainCircuit,
  CheckCircle2,
  Clock3,
  Lightbulb,
  Send,
  Sparkles,
} from 'lucide-react'

import {
  api,
} from '../api/profitlens'

import {
  SectionTitle,
} from '../components/SectionTitle'

import type {
  BusinessAnswerResponse,
} from '../types/api'

import {
  humanizeMetric,
} from '../utils'


const suggestions = [
  'Why did revenue decline?',
  'Which products generated the most revenue?',
  'What is our P90 delivery TAT?',
  'What should management focus on?',
  'Why did revenue fall even though delivery improved?',
  'What is our cancellation rate?',
]


type AnalystProps = {
  month: string
}


export default function Analyst({
  month,
}: AnalystProps) {
  const [
    question,
    setQuestion,
  ] = useState(
    'Why did revenue decline?'
  )

  const [
    data,
    setData,
  ] = useState<
    BusinessAnswerResponse | null
  >(null)

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState('')


  async function submit(
    event?: FormEvent
  ) {
    event?.preventDefault()

    const trimmed =
      question.trim()

    if (!trimmed) {
      return
    }

    setLoading(true)
    setError('')

    try {
      const result =
        await api.ask(
          trimmed,
          month
        )

      setData(
        result
      )

    } catch (err) {
      if (
        err instanceof Error
      ) {
        setError(
          err.message
        )
      } else {
        setError(
          'Unable to analyze the question.'
        )
      }

    } finally {
      setLoading(false)
    }
  }


  function chooseSuggestion(
    value: string
  ) {
    setQuestion(
      value
    )

    setError('')
  }


  return (
    <div className="page">

      <SectionTitle
        title="Ask ProfitLens"
        subtitle={
          `AI-assisted business analysis for ${month}. `
          + 'ProfitLens calculates the business facts first, then uses AI only to explain them.'
        }
      />


      <div className="analyst-workspace">

        <div className="analyst-left">

          <div className="card analyst-ask-card">

            <div className="analyst-ask-header">

              <div>

                <div className="card-title">
                  Ask a Business Question
                </div>

                <p>
                  Ask about revenue, orders, products,
                  customers, logistics or business health.
                </p>

              </div>

              <BrainCircuit
                size={20}
              />

            </div>


            <form
              onSubmit={submit}
              className="ask-form analyst-form-v2"
            >

              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target.value
                  )
                }
                placeholder="Example: Why did revenue decline?"
                disabled={loading}
              />

              <button
                type="submit"
                className="primary-btn"
                disabled={
                  loading
                  || !question.trim()
                }
              >

                {loading
                  ? (
                    <>
                      <Sparkles
                        size={15}
                        className="spin"
                      />
                      Analyzing…
                    </>
                  )
                  : (
                    <>
                      <Send
                        size={15}
                      />
                      Analyze
                    </>
                  )
                }

              </button>

            </form>


            <div className="analyst-suggestions">

              <span>
                Suggested questions
              </span>

              <div>

                {suggestions.map(
                  (suggestion) => (
                    <button
                      type="button"
                      key={suggestion}
                      onClick={() =>
                        chooseSuggestion(
                          suggestion
                        )
                      }
                      disabled={loading}
                    >
                      {suggestion}
                    </button>
                  )
                )}

              </div>

            </div>

          </div>


          {error && (
            <div className="notice error">
              {error}
            </div>
          )}


          {data && (
            <div className="card analyst-answer-card">

              <div className="analyst-answer-header">

                <div>

                  <span className="analyst-label">
                    ProfitLens conclusion
                  </span>

                  <h2>
                    {data.answer.answer}
                  </h2>

                </div>

                <CheckCircle2
                  size={22}
                />

              </div>


              <div className="analyst-meta-row">

                <span className="badge blue">
                  {humanizeMetric(
                    data.question_type
                  )}
                </span>


                <span
                  className={
                    `badge ${
                      data.ai_available
                        ? 'green'
                        : 'amber'
                    }`
                  }
                >
                  {
                    data.ai_available
                      ? 'AI interpretation'
                      : 'Deterministic fallback'
                  }
                </span>


                {
                  data.analysis_execution
                  && (
                    <span className="analyst-analysis-status">

                      <Clock3
                        size={13}
                      />

                      {
                        data.analysis_execution
                          .successful_steps
                      }
                      /
                      {
                        data.analysis_execution
                          .total_steps
                      }
                      {' '}
                      analysis completed

                    </span>
                  )
                }

              </div>


              {
                data.answer
                  .likely_driver
                && (
                  <div className="analyst-driver">

                    <div className="analyst-driver-icon">
                      <Lightbulb
                        size={18}
                      />
                    </div>

                    <div>

                      <span>
                        Likely driver
                      </span>

                      <strong>
                        {humanizeMetric(
                          data.answer
                            .likely_driver
                        )}
                      </strong>

                    </div>

                  </div>
                )
              }


              {
                data.answer
                  .evidence
                  ?.length > 0
                && (
                  <div className="analyst-section">

                    <div className="analyst-section-title">
                      Evidence
                    </div>

                    <div className="analyst-evidence-list">

                      {
                        data.answer
                          .evidence
                          .map(
                            (
                              evidence,
                              index
                            ) => (
                              <div
                                className="analyst-evidence-item"
                                key={
                                  `${evidence}-${index}`
                                }
                              >

                                <span>
                                  {index + 1}
                                </span>

                                <p>
                                  {evidence}
                                </p>

                              </div>
                            )
                          )
                      }

                    </div>

                  </div>
                )
              }


              {
                data.answer
                  .recommended_actions
                  ?.length > 0
                && (
                  <div className="analyst-section">

                    <div className="analyst-section-title">
                      Recommended Actions
                    </div>

                    <div className="analyst-action-list">

                      {
                        data.answer
                          .recommended_actions
                          .map(
                            (
                              action,
                              index
                            ) => (
                              <div
                                className="analyst-action-item"
                                key={
                                  `${action}-${index}`
                                }
                              >

                                <div>
                                  {index + 1}
                                </div>

                                <p>
                                  {action}
                                </p>

                              </div>
                            )
                          )
                      }

                    </div>

                  </div>
                )
              }

            </div>
          )}

        </div>


        <div className="analyst-right">

          <div className="card analyst-info-card">

            <div className="card-title">
              How ProfitLens Answers
            </div>


            <div className="analyst-process">

              <div>

                <span>
                  1
                </span>

                <div>
                  <strong>
                    Understand
                  </strong>

                  <p>
                    Classifies the business question.
                  </p>
                </div>

              </div>


              <div>

                <span>
                  2
                </span>

                <div>
                  <strong>
                    Calculate
                  </strong>

                  <p>
                    Runs deterministic analytics.
                  </p>
                </div>

              </div>


              <div>

                <span>
                  3
                </span>

                <div>
                  <strong>
                    Interpret
                  </strong>

                  <p>
                    AI explains the measured result.
                  </p>
                </div>

              </div>


              <div>

                <span>
                  4
                </span>

                <div>
                  <strong>
                    Guardrail
                  </strong>

                  <p>
                    Missing evidence stays unavailable.
                  </p>
                </div>

              </div>

            </div>

          </div>


          <div className="card analyst-info-card">

            <div className="card-title">
              Supported Questions
            </div>


            <div className="analyst-capabilities">

              <span>
                Revenue
              </span>

              <span>
                Orders
              </span>

              <span>
                AOV
              </span>

              <span>
                Products
              </span>

              <span>
                Customers
              </span>

              <span>
                Logistics
              </span>

              <span>
                Delivery
              </span>

              <span>
                Cancellations
              </span>

              <span>
                Business Health
              </span>

              <span>
                Scenarios
              </span>

            </div>

          </div>


          <div className="notice info">
            ProfitLens will not invent CAC, LTV,
            ROAS, RTO, contribution margin or other
            metrics when the required datasets are
            not connected.
          </div>

        </div>

      </div>

    </div>
  )
}
import {
  FormEvent,
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  Loader2,
  MessageSquareText,
  Sparkles,
} from 'lucide-react'

import {
  api,
} from '../api/profitlens'

import type {
  BusinessAnswerResponse,
} from '../types/api'


type AnalystProps = {
  month: string
}


const EXAMPLE_QUESTIONS = [
  'Why did revenue decline?',
  'Are we profitable after marketing?',
  'Is our marketing efficient?',
  'Why is RTO high?',
  'Which courier should we be concerned about?',
  'Which products generated the most revenue?',
  'What is our repeat customer rate?',
  'Which inventory problems require immediate action?',
  'What are the three biggest problems in the business?',
  'What should management focus on next?',
]


export default function Analyst({
  month,
}: AnalystProps) {
  const [
    question,
    setQuestion,
  ] = useState(
    'What should management focus on next?'
  )

  const [
    result,
    setResult,
  ] = useState<BusinessAnswerResponse | null>(
    null
  )

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  )


  useEffect(
    () => {
      setResult(null)
      setError(null)
    },
    [
      month,
    ]
  )


  const canSubmit =
    useMemo(
      () =>
        question.trim().length > 0
        && !loading,
      [
        question,
        loading,
      ]
    )


  async function askQuestion(
    submittedQuestion?: string,
  ) {
    const finalQuestion =
      (
        submittedQuestion
        ?? question
      ).trim()

    if (!finalQuestion) {
      return
    }

    setQuestion(
      finalQuestion
    )

    setLoading(true)
    setError(null)

    try {
      const response =
        await api.ask(
          finalQuestion,
          month,
        )

      setResult(
        response
      )

    } catch (
      requestError
    ) {
      setResult(null)

      setError(
        requestError
          instanceof Error
          ? requestError.message
          : 'Could not ask ProfitLens.'
      )

    } finally {
      setLoading(false)
    }
  }


  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    void askQuestion()
  }


  return (
    <div className="page">

      <div className="page-header">
        <div>
          <div className="eyebrow">
            AI business analyst
          </div>

          <h2>
            Ask ProfitLens
          </h2>

          <p>
            Ask business questions for {month}.
            ProfitLens calculates metrics deterministically
            and uses AI only to interpret the results.
          </p>
        </div>
      </div>


      <div className="card">

        <form
          onSubmit={
            handleSubmit
          }
        >
          <div className="analyst-input-wrap">

            <MessageSquareText
              size={20}
            />

            <textarea
              value={
                question
              }
              onChange={
                (
                  event
                ) =>
                  setQuestion(
                    event.target.value
                  )
              }
              placeholder="Ask a business question..."
              rows={4}
              disabled={
                loading
              }
            />

          </div>


          <div className="analyst-submit-row">

            <div className="analyst-hint">
              Example: Why is RTO high?
            </div>

            <button
              className="primary-button"
              type="submit"
              disabled={
                !canSubmit
              }
            >
              {
                loading
                  ? (
                    <>
                      <Loader2
                        size={16}
                      />
                      Analysing...
                    </>
                  )
                  : (
                    <>
                      <Sparkles
                        size={16}
                      />
                      Ask ProfitLens
                    </>
                  )
              }
            </button>

          </div>

        </form>

      </div>


      <div className="section-heading">
        <div>
          <h2>
            Try a question
          </h2>

          <p>
            Common founder and operator questions.
          </p>
        </div>
      </div>


      <div className="question-chip-grid">
        {
          EXAMPLE_QUESTIONS.map(
            (
              item
            ) => (
              <button
                key={
                  item
                }
                type="button"
                className="question-chip"
                onClick={
                  () => {
                    void askQuestion(
                      item
                    )
                  }
                }
                disabled={
                  loading
                }
              >
                {item}
              </button>
            )
          )
        }
      </div>


      {
        error
        && (
          <div className="card error-card">
            <AlertTriangle
              size={20}
            />

            <div>
              <strong>
                Could not complete analysis
              </strong>

              <p>
                {error}
              </p>
            </div>
          </div>
        )
      }


      {
        loading
        && (
          <div className="card analyst-loading">
            <Loader2
              size={22}
            />

            <div>
              <strong>
                Analysing {month}
              </strong>

              <p>
                ProfitLens is preparing deterministic
                business evidence and interpretation.
              </p>
            </div>
          </div>
        )
      }


      {
        result
        && !loading
        && (
          <div className="analyst-result-stack">

            <div className="card analyst-answer-card">

              <div className="analyst-answer-header">
                <div>
                  <div className="eyebrow">
                    Answer
                  </div>

                  <h3>
                    {
                      result.question
                    }
                  </h3>
                </div>

                <div
                  className={
                    result.ai_available
                      ? 'status-badge success'
                      : 'status-badge warning'
                  }
                >
                  {
                    result.ai_available
                      ? (
                        <>
                          <Bot
                            size={14}
                          />
                          AI interpreted
                        </>
                      )
                      : (
                        <>
                          <CheckCircle2
                            size={14}
                          />
                          Deterministic fallback
                        </>
                      )
                  }
                </div>
              </div>


              <div className="analyst-main-answer">
                {
                  result
                    .answer
                    .answer
                }
              </div>


              <div className="analyst-meta-row">

                <div>
                  <span>
                    Month
                  </span>

                  <strong>
                    {
                      result.month
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Intent
                  </span>

                  <strong>
                    {
                      result.question_type
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Analysis steps
                  </span>

                  <strong>
                    {
                      result.analysis_execution
                        ? `${result.analysis_execution.successful_steps}/${result.analysis_execution.total_steps}`
                        : '—'
                    }
                  </strong>
                </div>

              </div>

            </div>


            <div className="card">

              <div className="section-heading compact">
                <div>
                  <h3>
                    Evidence
                  </h3>

                  <p>
                    Deterministic facts supporting the answer.
                  </p>
                </div>
              </div>


              {
                result
                  .answer
                  .evidence
                  .length > 0
                  ? (
                    <div className="evidence-list">
                      {
                        result
                          .answer
                          .evidence
                          .map(
                            (
                              evidence,
                              index,
                            ) => (
                              <div
                                className="evidence-item"
                                key={
                                  `${evidence}-${index}`
                                }
                              >
                                <CheckCircle2
                                  size={16}
                                />

                                <span>
                                  {evidence}
                                </span>
                              </div>
                            )
                          )
                      }
                    </div>
                  )
                  : (
                    <div className="empty-state">
                      No supporting evidence was returned.
                    </div>
                  )
              }

            </div>


            <div className="card">

              <div className="section-heading compact">
                <div>
                  <h3>
                    Likely Driver
                  </h3>
                </div>
              </div>

              <p className="analyst-driver">
                {
                  result
                    .answer
                    .likely_driver
                }
              </p>

            </div>


            {
              result
                .answer
                .recommended_actions
                .length > 0
              && (
                <div className="card">

                  <div className="section-heading compact">
                    <div>
                      <h3>
                        Recommended Actions
                      </h3>

                      <p>
                        Actions based on the available evidence.
                      </p>
                    </div>
                  </div>


                  <div className="action-list">
                    {
                      result
                        .answer
                        .recommended_actions
                        .map(
                          (
                            action,
                            index,
                          ) => (
                            <div
                              className="action-item"
                              key={
                                `${action}-${index}`
                              }
                            >
                              <div className="action-number">
                                {
                                  index + 1
                                }
                              </div>

                              <span>
                                {action}
                              </span>
                            </div>
                          )
                        )
                    }
                  </div>

                </div>
              )
            }


            {
              !result.ai_available
              && (
                <div className="card limitation-card">

                  <AlertTriangle
                    size={20}
                  />

                  <div>
                    <strong>
                      AI interpretation unavailable
                    </strong>

                    <p>
                      ProfitLens returned a deterministic
                      analytical answer instead. Business
                      metrics remain available even when the
                      external AI service is rate-limited or
                      temporarily unavailable.
                    </p>
                  </div>

                </div>
              )
            }

          </div>
        )
      }


      <div className="card limitation-card">

        <div>
          <strong>
            Analytical guardrail
          </strong>

          <p>
            AI does not calculate ProfitLens financial
            or operational metrics. Revenue, profit,
            marketing, customer, logistics, product and
            inventory facts come from deterministic
            analytics. AI is used only for interpretation
            and evidence-based recommendations.
          </p>
        </div>

      </div>

    </div>
  )
}
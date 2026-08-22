import {
  type FormEvent,
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Bot,
  CheckCircle2,
  FlaskConical,
  Lightbulb,
  Loader2,
  MessageSquareText,
  PackageSearch,
  SearchCheck,
  ShieldCheck,
  Sparkles,
  Target,
  Users,
} from 'lucide-react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  api,
} from '../api/profitlens'

import type {
  BusinessAnswerResponse,
} from '../types/api'


type AnalystProps = {
  month: string
}


type Destination = {
  label: string
  path: string
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


const QUESTION_DESTINATIONS:
  Record<string, Destination> = {
    revenue: {
      label:
        'Open Revenue & Profit',
      path:
        '/revenue-profit',
    },

    orders: {
      label:
        'Open Business Health',
      path:
        '/',
    },

    product: {
      label:
        'Open Product Analysis',
      path:
        '/products',
    },

    customer: {
      label:
        'Open Customer Analysis',
      path:
        '/customers',
    },

    logistics: {
      label:
        'Open Logistics',
      path:
        '/logistics',
    },

    delivery: {
      label:
        'Open Logistics',
      path:
        '/logistics',
    },

    marketing: {
      label:
        'Open Marketing',
      path:
        '/marketing',
    },

    inventory: {
      label:
        'Open Inventory',
      path:
        '/inventory',
    },

    business_health: {
      label:
        'Open Business Health',
      path:
        '/',
    },

    performance: {
      label:
        'Open Business Health',
      path:
        '/',
    },

    trends: {
      label:
        'Open Business Health',
      path:
        '/',
    },
  }


const FOLLOW_UPS:
  Record<string, string[]> = {
    revenue: [
      'What is the biggest measurable driver of the revenue decline?',
      'Did orders or AOV contribute more to the revenue movement?',
      'What should management investigate first?',
    ],

    marketing: [
      'Which marketing channel is least efficient?',
      'Is CAC creating profitability pressure?',
      'What should we change in marketing first?',
    ],

    logistics: [
      'How much worse is COD RTO than prepaid RTO?',
      'Which courier should we be most concerned about?',
      'Which logistics problem should management fix first?',
    ],

    delivery: [
      'Which courier has the weakest delivery performance?',
      'Where is delivery performance creating the most risk?',
      'What should operations investigate first?',
    ],

    product: [
      'Which products generated the most revenue?',
      'Which products have the highest operational risk?',
      'Which products should management investigate first?',
    ],

    customer: [
      'What is our repeat customer rate?',
      'Which acquisition channels bring better-quality customers?',
      'Where is customer risk highest?',
    ],

    inventory: [
      'Where is the most working capital trapped?',
      'Which SKUs have the highest revenue at risk?',
      'Which inventory problems require immediate action?',
    ],

    business_health: [
      'What are the three biggest problems in the business?',
      'What is hurting profitability the most?',
      'What should management focus on next?',
    ],
  }


function humanizeIntent(
  value: string
) {
  return value
    .replaceAll(
      '_',
      ' '
    )
    .replace(
      /\b\w/g,
      character =>
        character.toUpperCase()
    )
}


export default function Analyst({
  month,
}: AnalystProps) {
  const navigate =
    useNavigate()

  const [
    question,
    setQuestion,
  ] = useState(
    'What should management focus on next?'
  )

  const [
    result,
    setResult,
  ] = useState<
    BusinessAnswerResponse | null
  >(
    null
  )

  const [
    loading,
    setLoading,
  ] = useState(
    false
  )

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(
    null
  )


  useEffect(
    () => {
      setResult(
        null
      )

      setError(
        null
      )
    },
    [
      month,
    ]
  )


  const canSubmit =
    useMemo(
      () =>
        question
          .trim()
          .length
        > 0
        && !loading,
      [
        question,
        loading,
      ]
    )


  const destination =
    useMemo(
      () => {
        if (
          !result
        ) {
          return {
            label:
              'Open Business Health',

            path:
              '/',
          }
        }

        return (
          QUESTION_DESTINATIONS[
            result.question_type
          ]
          ?? {
            label:
              'Open Business Health',

            path:
              '/',
          }
        )
      },
      [
        result,
      ]
    )


  const followUps =
    useMemo(
      () => {
        if (
          !result
        ) {
          return []
        }

        return (
          FOLLOW_UPS[
            result.question_type
          ]
          ?? FOLLOW_UPS
            .business_health
        )
      },
      [
        result,
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

    if (
      !finalQuestion
    ) {
      return
    }

    setQuestion(
      finalQuestion
    )

    setLoading(
      true
    )

    setError(
      null
    )

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
      setResult(
        null
      )

      setError(
        requestError
          instanceof Error
          ? requestError.message
          : (
              'Could not ask '
              + 'ProfitLens.'
            )
      )

    } finally {
      setLoading(
        false
      )
    }
  }


  function handleSubmit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    void askQuestion()
  }


  return (
    <div className="pl-analyst-v2">

      <section className="pl-business-hero">

        <div>

          <div className="pl-page-eyebrow">
            Decision intelligence
          </div>

          <h1>
            Ask ProfitLens
          </h1>

          <p>
            Investigate business performance
            for {month}. Metrics are calculated
            deterministically; AI is used only
            to interpret the evidence.
          </p>

        </div>


        <div className="pl-analyst-truth-badge">

          <ShieldCheck
            size={16}
          />

          <div>

            <strong>
              Deterministic truth layer
            </strong>

            <span>
              AI never calculates financial metrics
            </span>

          </div>

        </div>

      </section>


      <section className="pl-analyst-command">

        <form
          onSubmit={
            handleSubmit
          }
        >

          <div className="pl-analyst-input-wrap">

            <MessageSquareText
              size={19}
            />

            <textarea
              value={
                question
              }
              onChange={
                event =>
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


          <div className="pl-analyst-submit-row">

            <div className="pl-analyst-hint">

              <Sparkles
                size={13}
              />

              Ask what changed, why it changed,
              where the risk is, or what to do next.

            </div>


            <button
              className="pl-primary-button"
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
                          size={15}
                        />

                        Analysing...
                      </>
                    )
                  : (
                      <>
                        <Sparkles
                          size={15}
                        />

                        Ask ProfitLens
                      </>
                    )
              }

            </button>

          </div>

        </form>

      </section>


      <section>

        <div className="pl-section-header">

          <div>

            <h2>
              Suggested investigations
            </h2>

            <p>
              Start with a common founder
              or operator question.
            </p>

          </div>

        </div>


        <div className="pl-analyst-question-grid">

          {
            EXAMPLE_QUESTIONS.map(
              item => (
                <button
                  key={
                    item
                  }
                  type="button"
                  className="pl-analyst-question-chip"
                  onClick={() => {
                    void askQuestion(
                      item
                    )
                  }}
                  disabled={
                    loading
                  }
                >

                  <SearchCheck
                    size={14}
                  />

                  <span>
                    {item}
                  </span>

                  <ArrowRight
                    size={13}
                  />

                </button>
              )
            )
          }

        </div>

      </section>


      {
        error
        && (
          <section className="pl-page-state error">

            <AlertTriangle
              size={20}
            />

            <div>

              <strong>
                Could not complete analysis
              </strong>

              <span>
                {error}
              </span>

            </div>

          </section>
        )
      }


      {
        loading
        && (
          <section className="pl-analyst-loading">

            <Loader2
              size={22}
            />

            <div>

              <strong>
                Analysing {month}
              </strong>

              <span>
                Building deterministic business
                evidence and preparing an
                evidence-based interpretation.
              </span>

            </div>

          </section>
        )
      }


      {
        result
        && !loading
        && (
          <div className="pl-analyst-result-stack">

            <section className="pl-analyst-answer">

              <div className="pl-analyst-answer-header">

                <div>

                  <span className="pl-page-eyebrow">
                    Executive answer
                  </span>

                  <h2>
                    {
                      result.question
                    }
                  </h2>

                </div>


                <div
                  className={
                    result.ai_available
                      ? (
                          'pl-analyst-mode '
                          + 'ai'
                        )
                      : (
                          'pl-analyst-mode '
                          + 'deterministic'
                        )
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


              <div className="pl-analyst-meta">

                <div>

                  <span>
                    Reporting period
                  </span>

                  <strong>
                    {
                      result.month
                    }
                  </strong>

                </div>


                <div>

                  <span>
                    Question type
                  </span>

                  <strong>
                    {
                      humanizeIntent(
                        result
                          .question_type
                      )
                    }
                  </strong>

                </div>


                <div>

                  <span>
                    Execution
                  </span>

                  <strong>
                    {
                      result
                        .analysis_execution
                        ? (
                            `${result
                              .analysis_execution
                              .successful_steps}/`
                            + `${result
                              .analysis_execution
                              .total_steps}`
                          )
                        : '—'
                    }
                  </strong>

                </div>


                <div>

                  <span>
                    Failed steps
                  </span>

                  <strong>
                    {
                      result
                        .analysis_execution
                        ?.failed_steps
                      ?? 0
                    }
                  </strong>

                </div>

              </div>

            </section>


            {
              result.analysis_details
              && result
                .analysis_details
                .execution_results
                .length
              > 0
              && (
                <section className="pl-founder-panel">

                  <div className="pl-panel-header">

                    <div>

                      <span className="pl-page-eyebrow">
                        Deterministic analysis
                      </span>

                      <h2>
                        Analysis execution
                      </h2>

                    </div>


                    <div className="pl-analyst-execution-summary">

                      {
                        result
                          .analysis_execution
                          ?.successful_steps
                        ?? 0
                      }

                      /

                      {
                        result
                          .analysis_execution
                          ?.total_steps
                        ?? 0
                      }

                      {' complete'}

                    </div>

                  </div>


                  <div className="pl-analyst-execution-list">

                    {
                      result
                        .analysis_details
                        .execution_results
                        .map(
                          item => (
                            <div
                              key={
                                `${item.step}-${item.analysis}`
                              }
                              className="pl-analyst-execution-row"
                            >

                              <div className="pl-analyst-execution-step">
                                {
                                  String(
                                    item.step
                                  ).padStart(
                                    2,
                                    '0'
                                  )
                                }
                              </div>


                              <div className="pl-analyst-execution-copy">

                                <strong>
                                  {
                                    humanizeIntent(
                                      item.analysis
                                    )
                                  }
                                </strong>

                                <span>
                                  {
                                    item.reason
                                  }
                                </span>

                              </div>


                              <div
                                className={
                                  `pl-analyst-execution-status ${item.execution_status}`
                                }
                              >
                                {
                                  item.execution_status
                                }
                              </div>

                            </div>
                          )
                        )
                    }

                  </div>

                </section>
              )
            }


            {
              result.claim_analysis
              && result
                .claim_analysis
                .claims
                .length
              > 0
              && (
                <section className="pl-founder-panel">

                  <div className="pl-panel-header">

                    <div>

                      <span className="pl-page-eyebrow">
                        Evidence confidence
                      </span>

                      <h2>
                        What is known vs inferred
                      </h2>

                    </div>


                    <div className="pl-claim-summary">

                      <span>
                        {
                          result
                            .claim_analysis
                            .claim_counts
                            .fact
                        } facts
                      </span>

                      <span>
                        {
                          result
                            .claim_analysis
                            .claim_counts
                            .inference
                        } inferences
                      </span>

                    </div>

                  </div>


                  <div className="pl-claim-list">

                    {
                      result
                        .claim_analysis
                        .claims
                        .map(
                          claim => (
                            <div
                              key={
                                claim.claim_id
                              }
                              className="pl-claim-row"
                            >

                              <div className="pl-claim-row-top">

                                <div
                                  className={
                                    `pl-claim-type ${claim.claim_type}`
                                  }
                                >
                                  {
                                    claim
                                      .claim_type
                                  }
                                </div>


                                <div
                                  className={
                                    `pl-claim-confidence ${claim.confidence}`
                                  }
                                >
                                  {
                                    claim
                                      .confidence
                                  }

                                  {' confidence'}
                                </div>

                              </div>


                              <p>
                                {
                                  claim
                                    .statement
                                }
                              </p>


                              {
                                claim.limitation
                                && (
                                  <div className="pl-claim-limitation">

                                    <AlertTriangle
                                      size={13}
                                    />

                                    <span>
                                      {
                                        claim
                                          .limitation
                                      }
                                    </span>

                                  </div>
                                )
                              }

                            </div>
                          )
                        )
                    }

                  </div>


                  <div className="pl-claim-definition">

                    <ShieldCheck
                      size={14}
                    />

                    <span>
                      {
                        result
                          .claim_analysis
                          .confidence_definition
                      }
                    </span>

                  </div>

                </section>
              )
            }


            {
              result.hypothesis_analysis
              && result
                .hypothesis_analysis
                .hypotheses
                .length
              > 0
              && (
                <section className="pl-founder-panel">

                  <div className="pl-panel-header">

                    <div>

                      <span className="pl-page-eyebrow">
                        Evidence gaps
                      </span>

                      <h2>
                        What we still need to prove
                      </h2>

                    </div>


                    <div className="pl-hypothesis-summary">

                      <span>
                        {
                          result
                            .hypothesis_analysis
                            .hypothesis_count
                        } hypotheses
                      </span>

                      <span>
                        {
                          result
                            .hypothesis_analysis
                            .missing_evidence_count
                        } evidence gaps
                      </span>

                    </div>

                  </div>


                  <div className="pl-hypothesis-list">

                    {
                      result
                        .hypothesis_analysis
                        .hypotheses
                        .map(
                          hypothesis => (
                            <div
                              key={
                                hypothesis
                                  .hypothesis_id
                              }
                              className="pl-hypothesis-card"
                            >

                              <div className="pl-hypothesis-top">

                                <div>

                                  <span className="pl-hypothesis-domain">
                                    {
                                      humanizeIntent(
                                        hypothesis.domain
                                      )
                                    }
                                  </span>

                                  <h3>
                                    {
                                      hypothesis
                                        .statement
                                    }
                                  </h3>

                                </div>


                                <div
                                  className={
                                    `pl-hypothesis-status ${hypothesis.status}`
                                  }
                                >
                                  {
                                    humanizeIntent(
                                      hypothesis.status
                                    )
                                  }
                                </div>

                              </div>


                              <div className="pl-hypothesis-evidence-grid">

                                <div>

                                  <span className="pl-hypothesis-label">
                                    Current evidence
                                  </span>

                                  <div className="pl-hypothesis-evidence-list">

                                    {
                                      hypothesis
                                        .current_evidence
                                        .map(
                                          evidence => (
                                            <div
                                              key={
                                                `${hypothesis.hypothesis_id}-${evidence.metric}`
                                              }
                                            >
                                              <strong>
                                                {
                                                  humanizeIntent(
                                                    evidence.metric
                                                  )
                                                }
                                              </strong>

                                              <span>
                                                {
                                                  String(
                                                    evidence.value
                                                  )
                                                }
                                              </span>
                                            </div>
                                          )
                                        )
                                    }

                                  </div>

                                </div>


                                <div>

                                  <span className="pl-hypothesis-label">
                                    Missing evidence
                                  </span>

                                  <div className="pl-hypothesis-missing-list">

                                    {
                                      hypothesis
                                        .missing_evidence
                                        .map(
                                          missing => (
                                            <div
                                              key={
                                                missing
                                                  .evidence_id
                                              }
                                            >

                                              <AlertTriangle
                                                size={13}
                                              />

                                              <div>

                                                <strong>
                                                  {
                                                    missing
                                                      .description
                                                  }
                                                </strong>

                                                <span>
                                                  {
                                                    missing
                                                      .reason
                                                  }
                                                </span>

                                              </div>

                                            </div>
                                          )
                                        )
                                    }

                                  </div>

                                </div>

                              </div>


                              <div className="pl-hypothesis-test">

                                <span>
                                  How to test
                                </span>

                                <strong>
                                  {
                                    hypothesis
                                      .test
                                  }
                                </strong>

                              </div>

                            </div>
                          )
                        )
                    }

                  </div>


                  <div className="pl-hypothesis-guardrail">

                    <ShieldCheck
                      size={14}
                    />

                    <span>
                      {
                        result
                          .hypothesis_analysis
                          .causal_guardrail
                      }
                    </span>

                  </div>

                </section>
              )
            }


            {
              result.recommendation_analysis
              && result
                .recommendation_analysis
                .recommendations
                .length
              > 0
              && (
                <section className="pl-founder-panel">

                  <div className="pl-panel-header">

                    <div>

                      <span className="pl-page-eyebrow">
                        Action readiness
                      </span>

                      <h2>
                        Recommended next moves
                      </h2>

                    </div>


                    <div className="pl-recommendation-summary">

                      <span>
                        {
                          result
                            .recommendation_analysis
                            .readiness_counts
                            .act_now
                        } act now
                      </span>

                      <span>
                        {
                          result
                            .recommendation_analysis
                            .readiness_counts
                            .test_first
                        } test first
                      </span>

                      <span>
                        {
                          result
                            .recommendation_analysis
                            .readiness_counts
                            .investigate_first
                        } investigate
                      </span>

                      <span>
                        {
                          result
                            .recommendation_analysis
                            .readiness_counts
                            .do_not_act
                        } do not act
                      </span>

                    </div>

                  </div>


                  <div className="pl-recommendation-list">

                    {
                      result
                        .recommendation_analysis
                        .recommendations
                        .map(
                          item => (
                            <div
                              key={
                                item
                                  .recommendation_id
                              }
                              className="pl-recommendation-card"
                            >

                              <div className="pl-recommendation-top">

                                <div>

                                  <span className="pl-recommendation-domain">
                                    {
                                      humanizeIntent(
                                        item.domain
                                      )
                                    }
                                  </span>

                                  <h3>
                                    {
                                      item.action
                                    }
                                  </h3>

                                </div>


                                <div
                                  className={
                                    `pl-recommendation-readiness ${item.readiness}`
                                  }
                                >
                                  {
                                    item.readiness
                                    === 'act_now'
                                      ? 'Act now'
                                      : item.readiness
                                        === 'test_first'
                                        ? 'Test first'
                                        : item.readiness
                                          === 'investigate_first'
                                          ? 'Investigate first'
                                          : 'Do not act yet'
                                  }
                                </div>

                              </div>


                              <div className="pl-recommendation-rationale">

                                <span>
                                  Why
                                </span>

                                <p>
                                  {
                                    item.rationale
                                  }
                                </p>

                              </div>


                              {
                                item.guardrail
                                && (
                                  <div className="pl-recommendation-guardrail">

                                    <AlertTriangle
                                      size={13}
                                    />

                                    <span>
                                      {
                                        item.guardrail
                                      }
                                    </span>

                                  </div>
                                )
                              }


                              {
                                item.next_step
                                && (
                                  <div className="pl-recommendation-next">

                                    <span>
                                      Next step
                                    </span>

                                    <strong>
                                      {
                                        item.next_step
                                      }
                                    </strong>

                                  </div>
                                )
                              }

                            </div>
                          )
                        )
                    }

                  </div>


                  <div className="pl-recommendation-definition">

                    <ShieldCheck
                      size={14}
                    />

                    <span>
                      {
                        result
                          .recommendation_analysis
                          .guardrail
                      }
                    </span>

                  </div>

                </section>
              )
            }


            <section className="pl-analyst-insight-grid">

              <div className="pl-founder-panel">

                <div className="pl-panel-header">

                  <div>

                    <span className="pl-page-eyebrow">
                      Measured evidence
                    </span>

                    <h2>
                      What supports the answer
                    </h2>

                  </div>

                  <SearchCheck
                    size={18}
                  />

                </div>


                {
                  result
                    .answer
                    .evidence
                    .length
                  > 0
                    ? (
                        <div className="pl-analyst-evidence-list">

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
                                    key={
                                      `${evidence}-${index}`
                                    }
                                    className="pl-analyst-evidence"
                                  >

                                    <CheckCircle2
                                      size={15}
                                    />

                                    <span>
                                      {
                                        evidence
                                      }
                                    </span>

                                  </div>
                                )
                              )
                          }

                        </div>
                      )
                    : (
                        <div className="pl-empty-panel">
                          No supporting evidence
                          was returned.
                        </div>
                      )
                }

              </div>


              <div className="pl-founder-panel">

                <div className="pl-panel-header">

                  <div>

                    <span className="pl-page-eyebrow">
                      Driver assessment
                    </span>

                    <h2>
                      Likely driver
                    </h2>

                  </div>

                  <Target
                    size={18}
                  />

                </div>


                <div className="pl-analyst-driver">

                  <Lightbulb
                    size={18}
                  />

                  <p>
                    {
                      result
                        .answer
                        .likely_driver
                    }
                  </p>

                </div>

              </div>

            </section>


            {
              !result.recommendation_analysis
              && result
                .answer
                .recommended_actions
                .length
              > 0
              && (
                <section className="pl-founder-panel">

                  <div className="pl-panel-header">

                    <div>

                      <span className="pl-page-eyebrow">
                        Recommended next moves
                      </span>

                      <h2>
                        Actions
                      </h2>

                    </div>

                  </div>


                  <div className="pl-analyst-action-list">

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
                              key={
                                `${action}-${index}`
                              }
                              className="pl-analyst-action"
                            >

                              <div>
                                {
                                  String(
                                    index + 1
                                  ).padStart(
                                    2,
                                    '0'
                                  )
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

                </section>
              )
            }


            <section className="pl-founder-panel">

              <div className="pl-panel-header">

                <div>

                  <span className="pl-page-eyebrow">
                    Continue investigation
                  </span>

                  <h2>
                    Go deeper
                  </h2>

                </div>

              </div>


              <div className="pl-analyst-navigation">

                <button
                  type="button"
                  onClick={() =>
                    navigate(
                      destination.path
                    )
                  }
                >

                  {
                    result.question_type
                    === 'product'
                      ? (
                          <PackageSearch
                            size={15}
                          />
                        )
                      : result.question_type
                        === 'customer'
                        ? (
                            <Users
                              size={15}
                            />
                          )
                        : (
                            <BarChart3
                              size={15}
                            />
                          )
                  }

                  {
                    destination.label
                  }

                </button>


                <button
                  type="button"
                  onClick={() =>
                    navigate(
                      '/investigations'
                    )
                  }
                >

                  <Target
                    size={15}
                  />

                  View Investigations

                </button>


                <button
                  type="button"
                  onClick={() =>
                    navigate(
                      '/scenario'
                    )
                  }
                >

                  <FlaskConical
                    size={15}
                  />

                  Test Scenario

                </button>

              </div>

            </section>


            {
              followUps.length
              > 0
              && (
                <section>

                  <div className="pl-section-header">

                    <div>

                      <h2>
                        Ask a follow-up
                      </h2>

                      <p>
                        Continue from the
                        current investigation.
                      </p>

                    </div>

                  </div>


                  <div className="pl-analyst-followups">

                    {
                      followUps.map(
                        item => (
                          <button
                            key={
                              item
                            }
                            type="button"
                            onClick={() => {
                              void askQuestion(
                                item
                              )
                            }}
                          >

                            <MessageSquareText
                              size={14}
                            />

                            <span>
                              {item}
                            </span>

                            <ArrowRight
                              size={13}
                            />

                          </button>
                        )
                      )
                    }

                  </div>

                </section>
              )
            }


            {
              !result.ai_available
              && (
                <section className="pl-analyst-fallback-note">

                  <AlertTriangle
                    size={19}
                  />

                  <div>

                    <strong>
                      AI interpretation unavailable
                    </strong>

                    <p>
                      ProfitLens returned a
                      deterministic analytical
                      answer instead. Core business
                      metrics remain available even
                      when the external AI service
                      is unavailable.
                    </p>

                  </div>

                </section>
              )
            }

          </div>
        )
      }


      <section className="pl-analyst-guardrail">

        <ShieldCheck
          size={20}
        />

        <div>

          <strong>
            Analytical guardrail
          </strong>

          <p>
            Revenue, profit, marketing,
            customer, logistics, product and
            inventory facts come from
            deterministic analytics. AI may
            interpret those facts and recommend
            actions, but it does not calculate
            ProfitLens financial or operational
            truth.
          </p>

        </div>

      </section>

    </div>
  )
}

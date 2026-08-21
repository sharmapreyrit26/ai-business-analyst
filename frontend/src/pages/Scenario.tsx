import {
  FormEvent,
  useMemo,
  useState,
} from 'react'

import {
  ArrowRight,
  Calculator,
  Play,
  RefreshCw,
  TrendingUp,
} from 'lucide-react'

import {
  api,
} from '../api/profitlens'

import {
  SectionTitle,
} from '../components/SectionTitle'

import type {
  ScenarioResponse,
} from '../types/api'

import {
  fmtMoney,
  fmtNumber,
  humanizeMetric,
} from '../utils'


type ScenarioProps = {
  month: string
}


type ScenarioPayload = {
  period?: string
  scenario?: string
  status?: string

  assumptions?: Record<
    string,
    string | number | boolean | null
  >

  current?: {
    revenue?: number
    orders?: number
    aov?: number
  }

  scenario_result?: {
    revenue?: number
    orders?: number
    aov?: number
  }

  difference?: Record<
    string,
    number | null
  >

  limitations?: string[]
}


const presets = [
  {
    label: 'AOV +5%',
    question:
      'What if AOV increases by 5%?',
  },
  {
    label: 'AOV +12%',
    question:
      'What if AOV increases by 12%?',
  },
  {
    label: 'Recover 50% Orders',
    question:
      'What happens if we recover half of lost orders?',
  },
  {
    label: 'Orders +5%',
    question:
      'What happens if orders increase by 5%?',
  },
  {
    label: 'Orders +5%, AOV +5%',
    question:
      'What if orders increase by 5% and AOV increases by 5%?',
  },
]


export default function Scenario({
  month,
}: ScenarioProps) {
  const [
    question,
    setQuestion,
  ] = useState(
    'What if AOV increases by 12%?'
  )

  const [
    data,
    setData,
  ] = useState<
    ScenarioResponse | null
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

    const trimmedQuestion =
      question.trim()

    if (!trimmedQuestion) {
      return
    }

    setLoading(true)
    setError('')

    try {
      const result =
        await api.scenario(
          trimmedQuestion,
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
          'Unable to run scenario.'
        )
      }

    } finally {
      setLoading(false)
    }
  }


  const scenarioResult =
    data?.scenario_result as
      | ScenarioPayload
      | null
      | undefined


  const current =
    scenarioResult?.current
    ?? {}


  const simulated =
    scenarioResult
      ?.scenario_result
    ?? {}


  const difference =
    scenarioResult
      ?.difference
    ?? {}


  const assumptions =
    scenarioResult
      ?.assumptions
    ?? {}


  const limitations =
    scenarioResult
      ?.limitations
    ?? []


  const revenueImpact =
    difference
      .incremental_revenue


  const isPositive =
    Number(
      revenueImpact ?? 0
    ) >= 0


  const parameterRows =
    useMemo(
      () =>
        Object.entries(
          data?.parameters
          ?? {}
        ),
      [data]
    )


  return (
    <div className="page">

      <SectionTitle
        title="Scenario Lab"
        subtitle={
          `Deterministic what-if analysis for ${month}. `
          + 'Scenario outputs are calculations based on explicit assumptions, not forecasts.'
        }
      />


      <div className="card scenario-builder">

        <div className="scenario-builder-header">

          <div>

            <div className="card-title">
              Build a Scenario
            </div>

            <p>
              Ask ProfitLens how revenue changes
              when orders or AOV move.
            </p>

          </div>

          <Calculator
            size={19}
          />

        </div>


        <form
          onSubmit={submit}
          className="scenario-form-v2"
        >

          <input
            value={question}
            onChange={(event) =>
              setQuestion(
                event.target.value
              )
            }
            placeholder="Example: What if AOV increases by 10%?"
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
                  <RefreshCw
                    size={15}
                    className="spin"
                  />
                  Running…
                </>
              )
              : (
                <>
                  <Play
                    size={15}
                  />
                  Run Scenario
                </>
              )
            }

          </button>

        </form>


        <div className="scenario-presets">

          <span>
            Quick scenarios
          </span>

          <div>

            {presets.map(
              (preset) => (
                <button
                  key={
                    preset.label
                  }
                  type="button"
                  onClick={() =>
                    setQuestion(
                      preset.question
                    )
                  }
                  disabled={loading}
                >
                  {preset.label}
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
        <>

          <div className="scenario-status-row">

            <div className="card scenario-status-card">

              <span>
                Scenario Type
              </span>

              <strong>
                {humanizeMetric(
                  data.scenario_type
                  || 'scenario'
                )}
              </strong>

            </div>


            <div className="card scenario-status-card">

              <span>
                Status
              </span>

              <strong>
                {humanizeMetric(
                  data.status
                )}
              </strong>

            </div>


            <div className="card scenario-status-card">

              <span>
                Reporting Period
              </span>

              <strong>
                {data.month}
              </strong>

            </div>


            <div className="card scenario-status-card">

              <span>
                Revenue Impact
              </span>

              <strong
                className={
                  isPositive
                    ? 'positive-text'
                    : 'negative-text'
                }
              >
                {
                  revenueImpact
                    !== undefined
                    && revenueImpact
                    !== null
                    ? fmtMoney(
                      Number(
                        revenueImpact
                      )
                    )
                    : 'N/A'
                }
              </strong>

            </div>

          </div>


          <div className="scenario-comparison-grid">

            <div className="card">

              <div className="scenario-card-header">

                <div>

                  <div className="card-title">
                    Current Business
                  </div>

                  <p>
                    Actual values before applying
                    the scenario.
                  </p>

                </div>

              </div>


              <div className="metric-list">

                {
                  current.revenue
                    !== undefined
                  && (
                    <div>

                      <span>
                        Revenue
                      </span>

                      <strong>
                        {fmtMoney(
                          current.revenue
                        )}
                      </strong>

                    </div>
                  )
                }


                {
                  current.orders
                    !== undefined
                  && (
                    <div>

                      <span>
                        Orders
                      </span>

                      <strong>
                        {fmtNumber(
                          current.orders
                        )}
                      </strong>

                    </div>
                  )
                }


                {
                  current.aov
                    !== undefined
                  && (
                    <div>

                      <span>
                        AOV
                      </span>

                      <strong>
                        {fmtMoney(
                          current.aov
                        )}
                      </strong>

                    </div>
                  )
                }

              </div>

            </div>


            <div className="scenario-arrow">

              <ArrowRight
                size={24}
              />

            </div>


            <div className="card scenario-result-card">

              <div className="scenario-card-header">

                <div>

                  <div className="card-title">
                    Scenario Result
                  </div>

                  <p>
                    Estimated values after applying
                    the selected assumptions.
                  </p>

                </div>

                <TrendingUp
                  size={18}
                />

              </div>


              <div className="metric-list">

                {
                  simulated.revenue
                    !== undefined
                  && (
                    <div>

                      <span>
                        Revenue
                      </span>

                      <strong>
                        {fmtMoney(
                          simulated.revenue
                        )}
                      </strong>

                    </div>
                  )
                }


                {
                  simulated.orders
                    !== undefined
                  && (
                    <div>

                      <span>
                        Orders
                      </span>

                      <strong>
                        {fmtNumber(
                          simulated.orders
                        )}
                      </strong>

                    </div>
                  )
                }


                {
                  simulated.aov
                    !== undefined
                  && (
                    <div>

                      <span>
                        AOV
                      </span>

                      <strong>
                        {fmtMoney(
                          simulated.aov
                        )}
                      </strong>

                    </div>
                  )
                }

              </div>

            </div>

          </div>


          <div className="two-col">

            <div className="card">

              <div className="card-title">
                Estimated Impact
              </div>


              <div className="metric-list">

                {Object.entries(
                  difference
                ).map(
                  (
                    [
                      key,
                      value,
                    ]
                  ) => (

                    <div
                      key={key}
                    >

                      <span>
                        {humanizeMetric(
                          key
                        )}
                      </span>

                      <strong>
                        {
                          value === null
                            ? 'N/A'
                            : key.includes(
                              'revenue'
                            )
                              ? fmtMoney(
                                Number(
                                  value
                                )
                              )
                              : fmtNumber(
                                Number(
                                  value
                                )
                              )
                        }
                      </strong>

                    </div>

                  )
                )}

              </div>

            </div>


            <div className="card">

              <div className="card-title">
                Assumptions
              </div>


              <div className="metric-list">

                {Object.entries(
                  assumptions
                ).map(
                  (
                    [
                      key,
                      value,
                    ]
                  ) => (

                    <div
                      key={key}
                    >

                      <span>
                        {humanizeMetric(
                          key
                        )}
                      </span>

                      <strong>
                        {
                          value === null
                            ? 'N/A'
                            : key.includes(
                              'percent'
                            )
                              ? `${value}%`
                              : key.includes(
                                'aov'
                              )
                                ? fmtMoney(
                                  Number(
                                    value
                                  )
                                )
                                : typeof value === 'number'
                                  ? fmtNumber(
                                    value
                                  )
                                  : String(
                                    value
                                  )
                        }
                      </strong>

                    </div>

                  )
                )}

              </div>


              {
                parameterRows.length > 0
                && (
                  <div className="scenario-parser-note">

                    <span>
                      Parsed from question
                    </span>

                    <div>

                      {
                        parameterRows.map(
                          (
                            [
                              key,
                              value,
                            ]
                          ) => (
                            <code
                              key={key}
                            >
                              {
                                humanizeMetric(
                                  key
                                )
                              }
                              :
                              {' '}
                              {
                                String(
                                  value
                                )
                              }
                            </code>
                          )
                        )
                      }

                    </div>

                  </div>
                )
              }

            </div>

          </div>


          {
            limitations.length > 0
            && (
              <div className="notice warning">

                <strong>
                  Scenario limitations
                </strong>

                <ul>

                  {
                    limitations.map(
                      (
                        limitation,
                        index
                      ) => (
                        <li
                          key={
                            `${limitation}-${index}`
                          }
                        >
                          {limitation}
                        </li>
                      )
                    )
                  }

                </ul>

              </div>
            )
          }


          <div className="scenario-principle">

            <Calculator
              size={17}
            />

            <p>
              ProfitLens scenarios are deterministic
              sensitivity calculations. They show what the
              financial result would be under the specified
              assumptions; they do not predict whether
              customers will actually behave that way.
            </p>

          </div>

        </>
      )}

    </div>
  )
}
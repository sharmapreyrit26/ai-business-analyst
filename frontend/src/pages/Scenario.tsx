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

import { api } from '../api/profitlens'

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


type MetricValue =
  | string
  | number
  | boolean
  | null
  | undefined


type ScenarioPayload = {
  period?: string

  scenario?: string

  status?: string

  message?: string

  assumptions?: Record<
    string,
    MetricValue
  >

  current?: Record<
    string,
    MetricValue
  >

  scenario_result?: Record<
    string,
    MetricValue
  >

  difference?: Record<
    string,
    MetricValue
  >

  limitations?: string[]
}


const presets = [
  {
    label: 'AOV +10%',
    question: (
      'What if AOV increases by 10%?'
    ),
  },

  {
    label: 'Orders +10%',
    question: (
      'What if orders increase by 10%?'
    ),
  },

  {
    label: 'Orders +10%, AOV +5%',
    question: (
      'What if orders increase by 10% '
      + 'and AOV increases by 5%?'
    ),
  },

  {
    label: 'Recover 50% Lost Orders',
    question: (
      'What happens if we recover '
      + 'half of lost orders?'
    ),
  },

  {
    label: 'RTO -20%',
    question: (
      'What if RTO reduces by 20%?'
    ),
  },

  {
    label: 'Marketing Spend -15%',
    question: (
      'What if marketing spend '
      + 'decreases by 15%?'
    ),
  },

  {
    label: 'CAC -10%',
    question: (
      'What if CAC decreases by 10%?'
    ),
  },

  {
    label: 'Orders +10%, AOV +5%, RTO -20%',
    question: (
      'What if orders increase by 10%, '
      + 'AOV increases by 5%, '
      + 'and RTO reduces by 20%?'
    ),
  },
]


const MONEY_KEYS = new Set([
  'revenue',
  'aov',
  'gross_profit',
  'contribution_profit_before_marketing',
  'contribution_profit_after_marketing',
  'marketing_spend',
  'incremental_revenue',
  'marketing_spend_change',
  'incremental_contribution_profit_after_marketing',
  'cac',
  'cac_change',
])


const PERCENT_KEYS = new Set([
  'contribution_margin_after_marketing_percent',
  'rto_rate_percent',
  'rto_rate_change_percentage_points',
  'order_change_percent',
  'aov_change_percent',
  'marketing_spend_change_percent',
  'rto_reduction_percent',
  'recovery_percent',
  'cac_change_percent',
])


const INTEGERISH_KEYS = new Set([
  'orders',
  'additional_orders',
  'recovered_orders',
  'rto_orders',
  'recovered_rto_orders',
  'new_customers',
  'additional_new_customers',
])


function formatMetricValue(
  key: string,
  value: MetricValue,
) {
  if (
    value === null
    || value === undefined
  ) {
    return 'N/A'
  }

  if (
    typeof value === 'boolean'
  ) {
    return value
      ? 'Yes'
      : 'No'
  }

  if (
    typeof value === 'string'
  ) {
    return value
  }

  if (
    MONEY_KEYS.has(
      key
    )
  ) {
    return fmtMoney(
      Number(
        value
      )
    )
  }

  if (
    PERCENT_KEYS.has(
      key
    )
  ) {
    if (
      key === (
        'rto_rate_change_percentage_points'
      )
    ) {
      return (
        `${Number(value).toFixed(2)} pp`
      )
    }

    return (
      `${Number(value).toFixed(2)}%`
    )
  }

  if (
    INTEGERISH_KEYS.has(
      key
    )
  ) {
    return fmtNumber(
      Number(
        value
      )
    )
  }

  if (
    typeof value === 'number'
  ) {
    return fmtNumber(
      value
    )
  }

  return String(
    value
  )
}


function MetricList({
  metrics,
}: {
  metrics: Record<
    string,
    MetricValue
  >
}) {
  const entries = Object.entries(
    metrics
  )

  if (
    entries.length === 0
  ) {
    return (
      <div className="empty-state">
        No metrics available.
      </div>
    )
  }

  return (
    <div className="metric-list">
      {
        entries.map(
          ([
            key,
            value,
          ]) => (
            <div
              key={
                key
              }
            >
              <span>
                {
                  humanizeMetric(
                    key
                  )
                }
              </span>

              <strong>
                {
                  formatMetricValue(
                    key,
                    value,
                  )
                }
              </strong>
            </div>
          )
        )
      }
    </div>
  )
}


export default function Scenario({
  month,
}: ScenarioProps) {
  const [
    question,
    setQuestion,
  ] = useState(
    'What if orders increase by 10%, '
    + 'AOV increases by 5%, '
    + 'and RTO reduces by 20%?'
  )

  const [
    data,
    setData,
  ] = useState<
    ScenarioResponse
    | null
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
  ] = useState(
    ''
  )


  async function submit(
    event?: FormEvent,
  ) {
    event?.preventDefault()

    const trimmedQuestion =
      question.trim()

    if (
      !trimmedQuestion
    ) {
      return
    }

    setLoading(
      true
    )

    setError(
      ''
    )

    try {
      const result =
        await api.scenario(
          trimmedQuestion,
          month,
        )

      setData(
        result
      )

    } catch (
      err
    ) {
      setData(
        null
      )

      setError(
        err
          instanceof Error
          ? err.message
          : 'Unable to run scenario.'
      )

    } finally {
      setLoading(
        false
      )
    }
  }


  const scenarioPayload =
    data?.scenario_result as
      | ScenarioPayload
      | null
      | undefined


  const current =
    scenarioPayload?.current
    ?? {}


  const simulated =
    scenarioPayload
      ?.scenario_result
    ?? {}


  const difference =
    scenarioPayload?.difference
    ?? {}


  const assumptions =
    scenarioPayload?.assumptions
    ?? {}


  const limitations =
    scenarioPayload?.limitations
    ?? []


  const parameterRows =
    useMemo(
      () =>
        Object.entries(
          data?.parameters
          ?? {}
        ),
      [
        data,
      ]
    )


  const revenueImpact =
    typeof difference[
      'incremental_revenue'
    ] === 'number'
      ? Number(
        difference[
          'incremental_revenue'
        ]
      )
      : null


  const profitImpact =
    typeof difference[
      'incremental_contribution_profit_after_marketing'
    ] === 'number'
      ? Number(
        difference[
          'incremental_contribution_profit_after_marketing'
        ]
      )
      : null


  const isRevenuePositive =
    revenueImpact === null
      ? null
      : revenueImpact >= 0


  const isProfitPositive =
    profitImpact === null
      ? null
      : profitImpact >= 0


  return (
    <div className="page">

      <SectionTitle
        title="Scenario Lab"
        subtitle={
          `Deterministic what-if analysis for ${month}. `
          + 'Scenario outputs are sensitivity calculations '
          + 'based on explicit assumptions, not forecasts.'
        }
      />


      <div className="card scenario-builder">

        <div className="scenario-builder-header">

          <div>
            <div className="card-title">
              Build a Scenario
            </div>

            <p>
              Test how changes in orders,
              AOV, RTO, marketing spend,
              CAC and combined commercial
              assumptions affect the business.
            </p>
          </div>

          <Calculator
            size={19}
          />

        </div>


        <form
          onSubmit={
            submit
          }
          className="scenario-form-v2"
        >

          <input
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
            placeholder={
              'Example: What if orders increase by 10% '
              + 'and RTO falls by 20%?'
            }
            disabled={
              loading
            }
          />


          <button
            type="submit"
            className="primary-btn"
            disabled={
              loading
              || !question.trim()
            }
          >
            {
              loading
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
            {
              presets.map(
                (
                  preset
                ) => (
                  <button
                    key={
                      preset.label
                    }
                    type="button"
                    onClick={
                      () =>
                        setQuestion(
                          preset.question
                        )
                    }
                    disabled={
                      loading
                    }
                  >
                    {
                      preset.label
                    }
                  </button>
                )
              )
            }
          </div>

        </div>

      </div>


      {
        error
        && (
          <div className="notice error">
            {error}
          </div>
        )
      }


      {
        loading
        && (
          <div className="card analyst-loading">

            <RefreshCw
              size={20}
              className="spin"
            />

            <div>
              <strong>
                Running scenario
              </strong>

              <p>
                ProfitLens is applying the
                selected assumptions to
                deterministic business metrics.
              </p>
            </div>

          </div>
        )
      }


      {
        data
        && !loading
        && (
          <>

            <div className="scenario-status-row">

              <div className="card scenario-status-card">

                <span>
                  Scenario Type
                </span>

                <strong>
                  {
                    humanizeMetric(
                      data.scenario_type
                      || 'scenario'
                    )
                  }
                </strong>

              </div>


              <div className="card scenario-status-card">

                <span>
                  Status
                </span>

                <strong>
                  {
                    humanizeMetric(
                      data.status
                    )
                  }
                </strong>

              </div>


              <div className="card scenario-status-card">

                <span>
                  Reporting Period
                </span>

                <strong>
                  {
                    data.month
                  }
                </strong>

              </div>


              <div className="card scenario-status-card">

                <span>
                  Revenue Impact
                </span>

                <strong
                  className={
                    isRevenuePositive === null
                      ? ''
                      : isRevenuePositive
                        ? 'positive-text'
                        : 'negative-text'
                  }
                >
                  {
                    revenueImpact === null
                      ? 'N/A'
                      : fmtMoney(
                        revenueImpact
                      )
                  }
                </strong>

              </div>


              <div className="card scenario-status-card">

                <span>
                  Profit Impact
                </span>

                <strong
                  className={
                    isProfitPositive === null
                      ? ''
                      : isProfitPositive
                        ? 'positive-text'
                        : 'negative-text'
                  }
                >
                  {
                    profitImpact === null
                      ? 'N/A'
                      : fmtMoney(
                        profitImpact
                      )
                  }
                </strong>

              </div>

            </div>


            {
              scenarioPayload?.message
              && (
                <div className="notice warning">
                  {
                    scenarioPayload.message
                  }
                </div>
              )
            }


            <div className="scenario-comparison-grid">

              <div className="card">

                <div className="scenario-card-header">

                  <div>
                    <div className="card-title">
                      Current Business
                    </div>

                    <p>
                      Actual values before
                      applying the scenario.
                    </p>
                  </div>

                </div>


                <MetricList
                  metrics={
                    current
                  }
                />

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
                      Estimated values after
                      applying the selected
                      assumptions.
                    </p>
                  </div>

                  <TrendingUp
                    size={18}
                  />

                </div>


                <MetricList
                  metrics={
                    simulated
                  }
                />

              </div>

            </div>


            <div className="two-col">

              <div className="card">

                <div className="card-title">
                  Estimated Impact
                </div>


                <MetricList
                  metrics={
                    difference
                  }
                />

              </div>


              <div className="card">

                <div className="card-title">
                  Assumptions
                </div>


                <MetricList
                  metrics={
                    assumptions
                  }
                />


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
                            ([
                              key,
                              value,
                            ]) => (
                              <code
                                key={
                                  key
                                }
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
                          index,
                        ) => (
                          <li
                            key={
                              `${limitation}-${index}`
                            }
                          >
                            {
                              limitation
                            }
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
                sensitivity calculations. They show what
                the financial result would be if the
                specified assumptions held true. They do
                not predict whether customers, couriers
                or marketing channels will actually
                behave that way.
              </p>

            </div>

          </>
        )
      }

    </div>
  )
}
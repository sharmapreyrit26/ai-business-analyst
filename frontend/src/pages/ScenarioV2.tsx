import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  RefreshCcw,
  RotateCcw,
  Sparkles,
} from 'lucide-react'

import {
  apiV2,
} from '../api/v2/profitlens-v2'

import type {
  ScenarioControl,
  ScenarioV2Response,
} from '../api/v2/types'


type ScenarioV2Props = {
  month: string
}


type ScenarioValues = {
  orders_change_percent: number
  aov_change_percent: number
  rto_reduction_percent: number
  marketing_spend_change_percent: number
  cac_change_percent: number
  discount_rate_change_percent: number
}


const DEFAULT_VALUES:
  ScenarioValues = {
    orders_change_percent: 0,
    aov_change_percent: 0,
    rto_reduction_percent: 0,
    marketing_spend_change_percent: 0,
    cac_change_percent: 0,
    discount_rate_change_percent: 0,
  }


function formatMetric(
  key: string,
  value: unknown
) {
  if (
    typeof value
    !== 'number'
  ) {
    return String(
      value ?? '—'
    )
  }

  if (
    key.includes(
      'percent'
    )
  ) {
    return `${value.toFixed(2)}%`
  }

  if (
    key.includes(
      'revenue'
    )
    || key.includes(
      'profit'
    )
    || key.includes(
      'spend'
    )
    || key.includes(
      'cost'
    )
  ) {
    return new Intl.NumberFormat(
      'en-IN',
      {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0,
      }
    ).format(
      value
    )
  }

  return new Intl.NumberFormat(
    'en-IN',
    {
      maximumFractionDigits: 2,
    }
  ).format(
    value
  )
}


function humanize(
  value: string
) {
  return value
    .replace(
      /_/g,
      ' '
    )
    .replace(
      /\b\w/g,
      character =>
        character.toUpperCase()
    )
}


export default function ScenarioV2({
  month,
}: ScenarioV2Props) {
  const [
    controls,
    setControls,
  ] = useState<
    ScenarioControl[]
  >([])

  const [
    values,
    setValues,
  ] = useState<
    ScenarioValues
  >(
    DEFAULT_VALUES
  )

  const [
    result,
    setResult,
  ] = useState<
    ScenarioV2Response | null
  >(null)

  const [
    loading,
    setLoading,
  ] = useState(
    false
  )

  const [
    capabilitiesLoading,
    setCapabilitiesLoading,
  ] = useState(
    true
  )

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null)


  useEffect(
    () => {
      let cancelled =
        false

      setCapabilitiesLoading(
        true
      )

      apiV2
        .scenarioCapabilities()
        .then(
          response => {
            if (
              cancelled
            ) {
              return
            }

            setControls(
              response.controls
            )
          }
        )
        .catch(
          requestError => {
            if (
              cancelled
            ) {
              return
            }

            setError(
              requestError
                instanceof Error
                ? requestError.message
                : (
                    'Could not load '
                    + 'scenario controls.'
                  )
            )
          }
        )
        .finally(
          () => {
            if (
              !cancelled
            ) {
              setCapabilitiesLoading(
                false
              )
            }
          }
        )


      return () => {
        cancelled = true
      }
    },
    []
  )


  useEffect(
    () => {
      setResult(null)
      setError(null)
      setValues(
        DEFAULT_VALUES
      )
    },
    [
      month,
    ]
  )


  const hasChanges =
    useMemo(
      () =>
        Object
          .values(
            values
          )
          .some(
            value =>
              value !== 0
          ),
      [
        values,
      ]
    )


  function updateValue(
    key:
      keyof ScenarioValues,

    value: number
  ) {
    setValues(
      current => ({
        ...current,
        [key]:
          value,
      })
    )
  }


  function resetScenario() {
    setValues(
      DEFAULT_VALUES
    )

    setResult(null)
    setError(null)
  }


  async function runScenario() {
    setLoading(true)
    setError(null)

    try {
      const response =
        await apiV2
          .runScenario({
            month,

            changes: {
              ...values,
            },
          })

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
          : (
              'Could not run '
              + 'scenario.'
            )
      )

    } finally {
      setLoading(false)
    }
  }


  if (
    capabilitiesLoading
  ) {
    return (
      <div className="pl-scenario-v2">

        <div className="pl-page-state">
          <RefreshCcw
            size={20}
          />

          Loading Scenario Lab...
        </div>

      </div>
    )
  }


  return (
    <div className="pl-scenario-v2">

      <section className="pl-business-hero">

        <div>

          <div className="pl-page-eyebrow">
            Deterministic what-if analysis
          </div>

          <h1>
            Scenario Lab
          </h1>

          <p>
            Change business assumptions and see the
            deterministic financial impact for {month}.
          </p>

        </div>


        <div className="pl-business-hero-actions">

          <button
            type="button"
            className="pl-secondary-button"
            onClick={
              resetScenario
            }
          >
            <RotateCcw
              size={14}
            />

            Reset
          </button>

          <button
            type="button"
            className="pl-primary-button"
            disabled={
              loading
              || !hasChanges
            }
            onClick={() =>
              void runScenario()
            }
          >
            <Sparkles
              size={14}
            />

            {
              loading
                ? 'Running...'
                : 'Run scenario'
            }
          </button>

        </div>

      </section>


      {
        error
        && (
          <div className="pl-scenario-error">

            <AlertTriangle
              size={18}
            />

            <span>
              {error}
            </span>

          </div>
        )
      }


      <section className="pl-scenario-layout">

        <div className="pl-scenario-controls-panel">

          <div className="pl-section-header">

            <div>
              <h2>
                Scenario controls
              </h2>

              <p>
                Adjust one or multiple business variables.
              </p>
            </div>

          </div>


          <div className="pl-scenario-controls-list">

            {
              controls.map(
                control => {
                  const key =
                    control.control_id as keyof ScenarioValues

                  const value =
                    values[key]
                    ?? 0

                  return (
                    <div
                      key={
                        control.control_id
                      }
                      className={
                        `pl-scenario-control ${
                          !control.enabled
                            ? 'disabled'
                            : ''
                        }`
                      }
                    >

                      <div className="pl-scenario-control-header">

                        <div>

                          <strong>
                            {
                              control.label
                            }
                          </strong>

                          {
                            control.description
                            && (
                              <span>
                                {
                                  control.description
                                }
                              </span>
                            )
                          }

                        </div>


                        <div className="pl-scenario-input-wrap">

                          <input
                            type="number"
                            value={
                              value
                            }
                            disabled={
                              !control.enabled
                            }
                            min={
                              control.minimum
                              ?? undefined
                            }
                            max={
                              control.maximum
                              ?? undefined
                            }
                            step={
                              control.step
                              ?? 1
                            }
                            onChange={
                              event =>
                                updateValue(
                                  key,
                                  Number(
                                    event
                                      .target
                                      .value
                                  )
                                )
                            }
                          />

                          <span>
                            %
                          </span>

                        </div>

                      </div>


                      <input
                        className="pl-scenario-slider"
                        type="range"
                        value={
                          value
                        }
                        disabled={
                          !control.enabled
                        }
                        min={
                          control.minimum
                          ?? -100
                        }
                        max={
                          control.maximum
                          ?? 100
                        }
                        step={
                          control.step
                          ?? 1
                        }
                        onChange={
                          event =>
                            updateValue(
                              key,
                              Number(
                                event
                                  .target
                                  .value
                              )
                            )
                        }
                      />


                      <div className="pl-scenario-range-labels">

                        <span>
                          {
                            control.minimum
                            ?? -100
                          }%
                        </span>

                        <strong>
                          {
                            value > 0
                              ? '+'
                              : ''
                          }
                          {value}%
                        </strong>

                        <span>
                          {
                            control.maximum
                            ?? 100
                          }%
                        </span>

                      </div>


                      {
                        control.limitation
                        && (
                          <div className="pl-scenario-limitation">
                            {
                              control.limitation
                            }
                          </div>
                        )
                      }

                    </div>
                  )
                }
              )
            }

          </div>

        </div>


        <div className="pl-scenario-results-panel">

          {
            !result
              ? (
                <div className="pl-scenario-empty">

                  <Sparkles
                    size={28}
                  />

                  <h2>
                    Build a scenario
                  </h2>

                  <p>
                    Adjust the controls and run the scenario
                    to compare current and projected business
                    performance.
                  </p>

                </div>
              )
              : (
                <>

                  <div className="pl-section-header">

                    <div>
                      <h2>
                        Scenario result
                      </h2>

                      <p>
                        Current vs projected business performance.
                      </p>
                    </div>

                  </div>


                  <div className="pl-scenario-comparison-grid">

                    {
                      Object
                        .keys(
                          result.projected
                        )
                        .filter(
                          key =>
                            typeof result
                              .projected[
                                key
                              ]
                            === 'number'
                        )
                        .slice(
                          0,
                          8
                        )
                        .map(
                          key => {
                            const current =
                              result.current[
                                key
                              ]

                            const projected =
                              result.projected[
                                key
                              ]

                            const difference =
                              (
                                typeof current
                                === 'number'
                                && typeof projected
                                === 'number'
                              )
                                ? (
                                    projected
                                    - current
                                  )
                                : null

                            return (
                              <div
                                key={
                                  key
                                }
                                className="pl-scenario-result-card"
                              >

                                <span>
                                  {
                                    humanize(
                                      key
                                    )
                                  }
                                </span>

                                <div className="pl-scenario-current-projected">

                                  <div>
                                    <small>
                                      Current
                                    </small>

                                    <strong>
                                      {
                                        formatMetric(
                                          key,
                                          current
                                        )
                                      }
                                    </strong>
                                  </div>

                                  <div>
                                    <small>
                                      Projected
                                    </small>

                                    <strong>
                                      {
                                        formatMetric(
                                          key,
                                          projected
                                        )
                                      }
                                    </strong>
                                  </div>

                                </div>


                                {
                                  difference !== null
                                  && (
                                    <div
                                      className={
                                        `pl-scenario-delta ${
                                          difference > 0
                                            ? 'positive'
                                            : difference < 0
                                              ? 'negative'
                                              : 'neutral'
                                        }`
                                      }
                                    >

                                      {
                                        difference > 0
                                          ? (
                                              <ArrowUpRight
                                                size={13}
                                              />
                                            )
                                          : difference < 0
                                            ? (
                                                <ArrowDownRight
                                                  size={13}
                                                />
                                              )
                                            : null
                                      }

                                      {
                                        difference > 0
                                          ? '+'
                                          : ''
                                      }

                                      {
                                        formatMetric(
                                          key,
                                          difference
                                        )
                                      }

                                    </div>
                                  )
                                }

                              </div>
                            )
                          }
                        )
                    }

                  </div>


                  {
                    result.waterfall.length
                    > 0
                    && (
                      <section className="pl-scenario-section">

                        <div className="pl-section-header">

                          <div>
                            <h2>
                              Impact waterfall
                            </h2>

                            <p>
                              What is driving the scenario change.
                            </p>
                          </div>

                        </div>


                        <div className="pl-waterfall-list">

                          {
                            result.waterfall.map(
                              item => (
                                <div
                                  key={
                                    item.driver_id
                                  }
                                  className="pl-waterfall-row"
                                >

                                  <span>
                                    {
                                      item.label
                                    }
                                  </span>

                                  <div
                                    className={
                                      `pl-waterfall-impact ${
                                        item.direction
                                      }`
                                    }
                                  >
                                    {
                                      item.formatted_impact
                                      ?? item.impact
                                      ?? '—'
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
                    result.explanations.length
                    > 0
                    && (
                      <section className="pl-scenario-section">

                        <div className="pl-section-header">

                          <div>
                            <h2>
                              Explanation
                            </h2>

                            <p>
                              Deterministic interpretation of the result.
                            </p>
                          </div>

                        </div>


                        <div className="pl-scenario-explanation-list">

                          {
                            result.explanations.map(
                              item => (
                                <article
                                  key={
                                    item.headline
                                  }
                                >
                                  <strong>
                                    {
                                      item.headline
                                    }
                                  </strong>

                                  <p>
                                    {
                                      item.explanation
                                    }
                                  </p>

                                  {
                                    item.evidence.length
                                    > 0
                                    && (
                                      <ul>

                                        {
                                          item.evidence.map(
                                            evidence => (
                                              <li
                                                key={
                                                  evidence
                                                }
                                              >
                                                {
                                                  evidence
                                                }
                                              </li>
                                            )
                                          )
                                        }

                                      </ul>
                                    )
                                  }

                                </article>
                              )
                            )
                          }

                        </div>

                      </section>
                    )
                  }


                  {
                    result.assumptions.length
                    > 0
                    && (
                      <section className="pl-scenario-section">

                        <div className="pl-section-header">

                          <div>
                            <h2>
                              Assumptions
                            </h2>

                            <p>
                              Conditions used in this what-if model.
                            </p>
                          </div>

                        </div>


                        <div className="pl-assumption-list">

                          {
                            result.assumptions.map(
                              assumption => (
                                <div
                                  key={
                                    assumption
                                  }
                                >
                                  {assumption}
                                </div>
                              )
                            )
                          }

                        </div>

                      </section>
                    )
                  }


                  {
                    result.limitations.length
                    > 0
                    && (
                      <section className="pl-scenario-section">

                        <div className="pl-section-header">

                          <div>
                            <h2>
                              Limitations
                            </h2>
                          </div>

                        </div>


                        <div className="pl-limitations">

                          {
                            result.limitations.map(
                              limitation => (
                                <p
                                  key={
                                    limitation
                                  }
                                >
                                  {
                                    limitation
                                  }
                                </p>
                              )
                            )
                          }

                        </div>

                      </section>
                    )
                  }

                </>
              )
          }

        </div>

      </section>

    </div>
  )
}

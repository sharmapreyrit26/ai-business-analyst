import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  CircleDollarSign,
  Filter,
  RefreshCcw,
  ShieldAlert,
  Sparkles,
} from 'lucide-react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  apiV2,
} from '../api/v2/profitlens-v2'

import type {
  Investigation,
  InvestigationListResponse,
} from '../api/v2/types'


type InvestigationsProps = {
  month: string
}


type SeverityFilter =
  | 'all'
  | 'critical'
  | 'warning'
  | 'info'


function severityRank(
  severity: string
) {
  if (severity === 'critical') {
    return 0
  }

  if (severity === 'warning') {
    return 1
  }

  return 2
}


export default function Investigations({
  month,
}: InvestigationsProps) {
  const navigate =
    useNavigate()

  const [
    data,
    setData,
  ] = useState<
    InvestigationListResponse | null
  >(null)

  const [
    loading,
    setLoading,
  ] = useState(
    true
  )

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null)

  const [
    severityFilter,
    setSeverityFilter,
  ] = useState<
    SeverityFilter
  >(
    'all'
  )


  useEffect(
    () => {
      let cancelled =
        false

      setLoading(true)
      setError(null)

      apiV2
        .investigations(
          month
        )
        .then(
          response => {
            if (
              cancelled
            ) {
              return
            }

            setData(
              response
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

            setData(null)

            setError(
              requestError
                instanceof Error
                ? requestError.message
                : (
                    'Could not load '
                    + 'investigations.'
                  )
            )
          }
        )
        .finally(
          () => {
            if (
              !cancelled
            ) {
              setLoading(
                false
              )
            }
          }
        )


      return () => {
        cancelled = true
      }
    },
    [
      month,
    ]
  )


  const investigations =
    useMemo(
      () => {
        const rows =
          data
            ?.data
            .slice()
          ?? []

        rows.sort(
          (
            first,
            second,
          ) =>
            severityRank(
              first.severity
            )
            - severityRank(
                second.severity
              )
        )

        if (
          severityFilter
          === 'all'
        ) {
          return rows
        }

        return rows.filter(
          item =>
            item.severity
            === severityFilter
        )
      },
      [
        data,
        severityFilter,
      ]
    )


  const counts =
    useMemo(
      () => {
        const rows =
          data?.data
          ?? []

        return {
          all:
            rows.length,

          critical:
            rows.filter(
              item =>
                item.severity
                === 'critical'
            ).length,

          warning:
            rows.filter(
              item =>
                item.severity
                === 'warning'
            ).length,

          info:
            rows.filter(
              item =>
                item.severity
                === 'info'
            ).length,
        }
      },
      [
        data,
      ]
    )


  function openInvestigation(
    investigation:
      Investigation
  ) {
    const target =
      investigation
        .related_pages?.[0]

    if (
      target
    ) {
      navigate(
        target
      )
    }
  }


  if (
    loading
  ) {
    return (
      <div className="pl-investigations-page">

        <div className="pl-page-state">
          <RefreshCcw
            size={20}
          />

          Loading investigations...
        </div>

      </div>
    )
  }


  if (
    error
  ) {
    return (
      <div className="pl-investigations-page">

        <div className="pl-page-state error">

          <AlertTriangle
            size={20}
          />

          <div>
            <strong>
              Could not load investigations
            </strong>

            <span>
              {error}
            </span>
          </div>

        </div>

      </div>
    )
  }


  return (
    <div className="pl-investigations-page">

      <section className="pl-business-hero">

        <div>

          <div className="pl-page-eyebrow">
            ProfitLens intelligence
          </div>

          <h1>
            Investigations
          </h1>

          <p>
            Prioritized business problems,
            deterministic evidence and next actions
            for {month}.
          </p>

        </div>


        <div className="pl-business-hero-actions">

          <button
            type="button"
            className="pl-secondary-button"
            onClick={() =>
              navigate(
                '/analyst'
              )
            }
          >
            <Sparkles
              size={14}
            />

            Ask ProfitLens
          </button>

          <button
            type="button"
            className="pl-primary-button"
            onClick={() =>
              navigate(
                '/scenario'
              )
            }
          >
            Test scenario
          </button>

        </div>

      </section>


      <section className="pl-investigation-summary-grid">

        <button
          type="button"
          className={
            `pl-investigation-summary-card ${
              severityFilter
              === 'all'
                ? 'active'
                : ''
            }`
          }
          onClick={() =>
            setSeverityFilter(
              'all'
            )
          }
        >
          <Filter
            size={17}
          />

          <div>
            <span>
              All investigations
            </span>

            <strong>
              {
                counts.all
              }
            </strong>
          </div>
        </button>


        <button
          type="button"
          className={
            `pl-investigation-summary-card critical ${
              severityFilter
              === 'critical'
                ? 'active'
                : ''
            }`
          }
          onClick={() =>
            setSeverityFilter(
              'critical'
            )
          }
        >
          <ShieldAlert
            size={17}
          />

          <div>
            <span>
              Critical
            </span>

            <strong>
              {
                counts.critical
              }
            </strong>
          </div>
        </button>


        <button
          type="button"
          className={
            `pl-investigation-summary-card warning ${
              severityFilter
              === 'warning'
                ? 'active'
                : ''
            }`
          }
          onClick={() =>
            setSeverityFilter(
              'warning'
            )
          }
        >
          <AlertTriangle
            size={17}
          />

          <div>
            <span>
              Warning
            </span>

            <strong>
              {
                counts.warning
              }
            </strong>
          </div>
        </button>


        <button
          type="button"
          className={
            `pl-investigation-summary-card info ${
              severityFilter
              === 'info'
                ? 'active'
                : ''
            }`
          }
          onClick={() =>
            setSeverityFilter(
              'info'
            )
          }
        >
          <CheckCircle2
            size={17}
          />

          <div>
            <span>
              Informational
            </span>

            <strong>
              {
                counts.info
              }
            </strong>
          </div>
        </button>

      </section>


      {
        investigations.length
        > 0
          ? (
            <section className="pl-investigation-board">

              {
                investigations.map(
                  (
                    item,
                    index,
                  ) => (
                    <article
                      key={
                        item.investigation_id
                      }
                      className="pl-investigation-card"
                    >

                      <div className="pl-investigation-card-index">
                        {
                          String(
                            index + 1
                          )
                            .padStart(
                              2,
                              '0'
                            )
                        }
                      </div>


                      <div className="pl-investigation-card-main">

                        <div className="pl-investigation-card-heading">

                          <div>

                            <div className="pl-investigation-title-row">

                              <h2>
                                {
                                  item.title
                                }
                              </h2>

                              <span
                                className={
                                  `pl-severity-badge ${
                                    item.severity
                                  }`
                                }
                              >
                                {
                                  item.severity
                                }
                              </span>

                            </div>


                            <p>
                              {
                                item.summary
                              }
                            </p>

                          </div>


                          {
                            item.formatted_impact
                            && (
                              <div className="pl-investigation-impact">

                                <CircleDollarSign
                                  size={15}
                                />

                                <div>
                                  <span>
                                    Estimated impact
                                  </span>

                                  <strong>
                                    {
                                      item.formatted_impact
                                    }
                                  </strong>
                                </div>

                              </div>
                            )
                          }

                        </div>


                        {
                          item.drivers.length
                          > 0
                          && (
                            <div className="pl-investigation-subsection">

                              <span className="pl-investigation-subtitle">
                                Likely drivers
                              </span>

                              <div className="pl-driver-grid">

                                {
                                  item.drivers.map(
                                    (
                                      driver,
                                      driverIndex,
                                    ) => {
                                      const typed =
                                        driver as {
                                          driver_id?: string
                                          label?: string
                                          evidence?: string[]
                                        }

                                      return (
                                        <div
                                          key={
                                            typed.driver_id
                                            ?? driverIndex
                                          }
                                          className="pl-driver-card"
                                        >
                                          <strong>
                                            {
                                              typed.label
                                              ?? 'Driver'
                                            }
                                          </strong>

                                          {
                                            typed
                                              .evidence
                                              ?.slice(
                                                0,
                                                2
                                              )
                                              .map(
                                                (
                                                  evidence,
                                                  evidenceIndex,
                                                ) => (
                                                  <span
                                                    key={
                                                      evidenceIndex
                                                    }
                                                  >
                                                    {
                                                      evidence
                                                    }
                                                  </span>
                                                )
                                              )
                                          }
                                        </div>
                                      )
                                    }
                                  )
                                }

                              </div>

                            </div>
                          )
                        }


                        {
                          item.recommended_actions.length
                          > 0
                          && (
                            <div className="pl-investigation-subsection">

                              <span className="pl-investigation-subtitle">
                                Recommended actions
                              </span>

                              <div className="pl-action-list">

                                {
                                  item
                                    .recommended_actions
                                    .slice(
                                      0,
                                      3
                                    )
                                    .map(
                                      (
                                        action,
                                        actionIndex,
                                      ) => {
                                        const typed =
                                          action as {
                                            action_id?: string
                                            label?: string
                                            priority?: number
                                            related_page?: string
                                          }

                                        return (
                                          <button
                                            key={
                                              typed.action_id
                                              ?? actionIndex
                                            }
                                            type="button"
                                            onClick={() => {
                                              if (
                                                typed.related_page
                                              ) {
                                                navigate(
                                                  typed.related_page
                                                )
                                              }
                                            }}
                                          >
                                            <span>
                                              {
                                                typed.priority
                                                ?? actionIndex + 1
                                              }
                                            </span>

                                            <strong>
                                              {
                                                typed.label
                                                ?? 'Review issue'
                                              }
                                            </strong>

                                            <ArrowRight
                                              size={14}
                                            />
                                          </button>
                                        )
                                      }
                                    )
                                }

                              </div>

                            </div>
                          )
                        }


                        {
                          item.scenario_suggestions.length
                          > 0
                          && (
                            <div className="pl-investigation-subsection">

                              <span className="pl-investigation-subtitle">
                                Scenario ideas
                              </span>

                              <div className="pl-chip-row">

                                {
                                  item
                                    .scenario_suggestions
                                    .map(
                                      question => (
                                        <button
                                          key={
                                            question
                                          }
                                          type="button"
                                          className="pl-chip-button"
                                          onClick={() =>
                                            navigate(
                                              '/scenario'
                                            )
                                          }
                                        >
                                          {
                                            question
                                          }
                                        </button>
                                      )
                                    )
                                }

                              </div>

                            </div>
                          )
                        }

                      </div>


                      <button
                        type="button"
                        className="pl-investigation-open"
                        onClick={() =>
                          openInvestigation(
                            item
                          )
                        }
                      >
                        Investigate

                        <ArrowRight
                          size={14}
                        />
                      </button>

                    </article>
                  )
                )
              }

            </section>
          )
          : (
            <section className="pl-investigation-empty">

              <CheckCircle2
                size={26}
              />

              <h2>
                No investigations in this view
              </h2>

              <p>
                No issues match the selected
                severity filter for {month}.
              </p>

            </section>
          )
      }

    </div>
  )
}

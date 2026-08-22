import {
  Database,
  ExternalLink,
  FileText,
  ShieldCheck,
  X,
} from 'lucide-react'

import type {
  MetricDrilldown,
} from '../../api/v2/types'


type MetricDrilldownDrawerProps = {
  open: boolean

  loading?: boolean

  error?: string | null

  data?: MetricDrilldown | null

  onClose: () => void

  onRelatedMetric?: (
    metricId: string
  ) => void

  onSuggestedQuestion?: (
    question: string
  ) => void
}


export function MetricDrilldownDrawer({
  open,
  loading = false,
  error = null,
  data = null,
  onClose,
  onRelatedMetric,
  onSuggestedQuestion,
}: MetricDrilldownDrawerProps) {
  if (!open) {
    return null
  }


  return (
    <>

      <button
        type="button"
        className="pl-drawer-backdrop"
        onClick={onClose}
        aria-label="Close metric details"
      />


      <aside className="pl-metric-drawer">

        <div className="pl-metric-drawer-header">

          <div>
            <span>
              Metric details
            </span>

            <h2>
              {
                data
                  ?.metric
                  .label
                ?? 'Loading metric'
              }
            </h2>
          </div>

          <button
            type="button"
            className="pl-icon-button"
            onClick={onClose}
            aria-label="Close metric drawer"
          >
            <X size={18} />
          </button>

        </div>


        <div className="pl-metric-drawer-body">

          {
            loading
            && (
              <div className="pl-drawer-state">
                Loading metric details...
              </div>
            )
          }


          {
            error
            && !loading
            && (
              <div className="pl-drawer-state error">
                {error}
              </div>
            )
          }


          {
            data
            && !loading
            && (
              <>

                <section className="pl-drilldown-hero">

                  <div className="pl-drilldown-value">
                    {
                      data
                        .metric
                        .formatted_value
                      ?? data
                        .metric
                        .value
                      ?? '—'
                    }
                  </div>

                  {
                    data
                      .metric
                      .comparison
                      .change_percent
                    !== null
                    && data
                      .metric
                      .comparison
                      .change_percent
                    !== undefined
                    && (
                      <div
                        className={
                          `pl-drilldown-change ${
                            data
                              .metric
                              .sentiment
                          }`
                        }
                      >
                        {
                          data
                            .metric
                            .comparison
                            .change_percent! > 0
                            ? '+'
                            : ''
                        }

                        {
                          data
                            .metric
                            .comparison
                            .change_percent!
                            .toFixed(
                              2
                            )
                        }%
                        {' '}
                        vs comparison
                      </div>
                    )
                  }

                </section>


                <section className="pl-drilldown-section">

                  <div className="pl-drilldown-section-title">
                    <FileText size={16} />

                    Definition
                  </div>

                  <p>
                    {
                      data
                        .metric
                        .definition
                      ?? 'No definition available.'
                    }
                  </p>

                </section>


                <section className="pl-drilldown-section">

                  <div className="pl-drilldown-section-title">
                    <FileText size={16} />

                    Calculation
                  </div>

                  <div className="pl-formula-box">
                    {
                      data
                        .metric
                        .formula
                      ?? 'No formula available.'
                    }
                  </div>


                  {
                    data
                      .calculation_components
                      .length > 0
                    && (
                      <div className="pl-calculation-components">

                        {
                          data
                            .calculation_components
                            .map(
                              component => (
                                <div
                                  key={
                                    component.component_id
                                  }
                                  className="pl-calculation-row"
                                >
                                  <span>
                                    {
                                      component.label
                                    }
                                  </span>

                                  <strong>
                                    {
                                      component.formatted_value
                                      ?? component.value
                                      ?? '—'
                                    }
                                  </strong>

                                  {
                                    component.operator
                                    && (
                                      <small>
                                        {
                                          component.operator
                                        }
                                      </small>
                                    )
                                  }
                                </div>
                              )
                            )
                        }

                      </div>
                    )
                  }

                </section>


                <section className="pl-drilldown-section">

                  <div className="pl-drilldown-section-title">
                    <Database size={16} />

                    Sources
                  </div>

                  <div className="pl-source-list">

                    {
                      data.sources.map(
                        (
                          source,
                          index,
                        ) => (
                          <div
                            key={
                              `${source.source_type}-${source.source_name}-${index}`
                            }
                            className="pl-source-row"
                          >
                            <div>
                              <strong>
                                {
                                  source.source_name
                                }
                              </strong>

                              <span>
                                {
                                  source.source_type
                                }
                              </span>
                            </div>

                            {
                              source.fields.length > 0
                              && (
                                <small>
                                  {
                                    source
                                      .fields
                                      .join(', ')
                                  }
                                </small>
                              )
                            }
                          </div>
                        )
                      )
                    }

                  </div>

                </section>


                <section className="pl-drilldown-section">

                  <div className="pl-drilldown-section-title">
                    <ShieldCheck size={16} />

                    Data quality
                  </div>

                  <div className="pl-quality-pill">
                    {
                      data.data_quality
                    }
                  </div>

                  {
                    data.limitations.length > 0
                    && (
                      <div className="pl-limitations">

                        {
                          data.limitations.map(
                            (
                              limitation,
                              index,
                            ) => (
                              <p
                                key={index}
                              >
                                {limitation}
                              </p>
                            )
                          )
                        }

                      </div>
                    )
                  }

                </section>


                {
                  data.related_metrics.length > 0
                  && (
                    <section className="pl-drilldown-section">

                      <div className="pl-drilldown-section-title">
                        Related metrics
                      </div>

                      <div className="pl-chip-row">

                        {
                          data.related_metrics.map(
                            metricId => (
                              <button
                                key={metricId}
                                type="button"
                                className="pl-chip-button"
                                onClick={() =>
                                  onRelatedMetric?.(
                                    metricId
                                  )
                                }
                              >
                                {
                                  metricId
                                }

                                <ExternalLink
                                  size={12}
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
                  data.suggested_questions.length > 0
                  && (
                    <section className="pl-drilldown-section">

                      <div className="pl-drilldown-section-title">
                        Ask ProfitLens
                      </div>

                      <div className="pl-question-list">

                        {
                          data
                            .suggested_questions
                            .map(
                              question => (
                                <button
                                  key={question}
                                  type="button"
                                  className="pl-question-button"
                                  onClick={() =>
                                    onSuggestedQuestion?.(
                                      question
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

                    </section>
                  )
                }

              </>
            )
          }

        </div>

      </aside>

    </>
  )
}

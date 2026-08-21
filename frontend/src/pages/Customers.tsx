import {
  useEffect,
  useState,
} from 'react'

import {
  AlertTriangle,
  CheckCircle2,
  Database,
  KeyRound,
  Repeat2,
  UserRound,
  Users,
  WalletCards,
} from 'lucide-react'

import {
  api,
} from '../api/profitlens'

import {
  ErrorState,
  LoadingState,
} from '../components/PageState'

import {
  SectionTitle,
} from '../components/SectionTitle'

import type {
  CustomerAnalyticsResponse,
} from '../types/api'

import {
  fmtNumber,
  fmtPct,
  humanizeMetric,
} from '../utils'


type CustomersProps = {
  month: string
}


export default function Customers({
  month,
}: CustomersProps) {
  const [
    data,
    setData,
  ] = useState<
    CustomerAnalyticsResponse | null
  >(null)

  const [
    error,
    setError,
  ] = useState('')


  useEffect(() => {
    let active = true

    setData(null)
    setError('')

    api.customers()
      .then((result) => {
        if (active) {
          setData(
            result
          )
        }
      })
      .catch((err) => {
        if (!active) {
          return
        }

        if (
          err instanceof Error
        ) {
          setError(
            err.message
          )
        } else {
          setError(
            'Unable to load customer analytics.'
          )
        }
      })

    return () => {
      active = false
    }

  }, [month])


  if (error) {
    return (
      <ErrorState
        error={error}
      />
    )
  }


  if (!data) {
    return (
      <LoadingState />
    )
  }


  const quality =
    data.data_quality || {}


  const available =
    data.available_analysis || {}


  const unavailable =
    data.unavailable_analysis || {}


  const nextRequirement =
    data.next_data_requirement || {}


  const customerSummary =
    available
      .customer_order_summary
      || {}


  const unavailableMetrics =
    Object.entries(
      unavailable
    )


  return (
    <div className="page">

      <SectionTitle
        title="Customer Analysis"
        subtitle={
          'Customer-data coverage, available metrics, '
          + 'and the additional data required for retention, '
          + 'repeat purchase and LTV analysis.'
        }
      />


      <div className="customer-status-banner">

        <div className="customer-status-icon">
          <AlertTriangle
            size={20}
          />
        </div>

        <div>
          <span>
            Customer analytics status
          </span>

          <strong>
            {humanizeMetric(
              data.status
            )}
          </strong>

          <p>
            ProfitLens can analyse the customer records
            currently available, but it will not fabricate
            retention or repeat-purchase metrics without a
            persistent customer identifier.
          </p>
        </div>

      </div>


      <div className="customer-kpi-grid">

        <div className="card customer-kpi">

          <div className="customer-kpi-icon blue">
            <Users
              size={18}
            />
          </div>

          <div>
            <span>
              Customer Records
            </span>

            <strong>
              {fmtNumber(
                quality.total_orders
              )}
            </strong>

            <small>
              Order-linked customer records
            </small>
          </div>

        </div>


        <div className="card customer-kpi">

          <div className="customer-kpi-icon green">
            <UserRound
              size={18}
            />
          </div>

          <div>
            <span>
              Unique Customer IDs
            </span>

            <strong>
              {fmtNumber(
                quality
                  .unique_customer_ids
              )}
            </strong>

            <small>
              IDs available in current dataset
            </small>
          </div>

        </div>


        <div className="card customer-kpi">

          <div className="customer-kpi-icon purple">
            <Database
              size={18}
            />
          </div>

          <div>
            <span>
              ID Coverage
            </span>

            <strong>
              {fmtPct(
                quality
                  .customer_id_coverage_percent
              )}
            </strong>

            <small>
              Records with customer ID
            </small>
          </div>

        </div>


        <div className="card customer-kpi">

          <div className="customer-kpi-icon red">
            <KeyRound
              size={18}
            />
          </div>

          <div>
            <span>
              Persistent ID
            </span>

            <strong>
              {
                quality
                  .persistent_customer_identifier_available
                  ? 'Available'
                  : 'Missing'
              }
            </strong>

            <small>
              Required for true retention
            </small>
          </div>

        </div>

      </div>


      <div className="two-col">

        <div className="card">

          <div className="card-title">
            Available Customer Analysis
          </div>


          <div className="metric-list">

            <div>
              <span>
                Customer records
              </span>

              <strong>
                {fmtNumber(
                  customerSummary
                    .customer_records
                )}
              </strong>
            </div>


            <div>
              <span>
                Avg orders per customer ID
              </span>

              <strong>
                {
                  customerSummary
                    .average_orders_per_customer_id
                  ?? 'N/A'
                }
              </strong>
            </div>


            <div>
              <span>
                Max orders for one customer ID
              </span>

              <strong>
                {fmtNumber(
                  customerSummary
                    .maximum_orders_for_single_customer_id
                )}
              </strong>
            </div>


            <div>
              <span>
                Missing customer IDs
              </span>

              <strong>
                {fmtNumber(
                  quality
                    .missing_customer_ids
                )}
              </strong>
            </div>

          </div>


          <div className="notice warning">
            {
              customerSummary
                .interpretation_warning
              || (
                'Current customer IDs should not be '
                + 'interpreted as persistent customer '
                + 'identities across multiple purchases.'
              )
            }
          </div>

        </div>


        <div className="card">

          <div className="card-title">
            Next Data Requirement
          </div>


          <div className="customer-next-data">

            <div className="customer-next-icon">
              <KeyRound
                size={20}
              />
            </div>


            <div>
              <span>
                Required dataset
              </span>

              <strong>
                {
                  nextRequirement
                    .dataset
                  || 'Customer master data'
                }
              </strong>
            </div>

          </div>


          <div className="customer-next-data">

            <div className="customer-next-icon">
              <Database
                size={20}
              />
            </div>


            <div>
              <span>
                Critical field
              </span>

              <strong className="mono">
                {
                  nextRequirement
                    .critical_field
                  || 'customer_unique_id'
                }
              </strong>
            </div>

          </div>


          <div className="notice info">
            {
              nextRequirement
                .reason
              || (
                'A persistent customer identifier is '
                + 'needed to connect multiple orders '
                + 'to the same underlying customer.'
              )
            }
          </div>

        </div>

      </div>


      <div className="card">

        <div className="customer-card-header">

          <div>

            <div className="card-title">
              Metrics Waiting for More Data
            </div>

            <p>
              ProfitLens explicitly marks these metrics
              unavailable rather than estimating them
              from incomplete data.
            </p>

          </div>

          <span className="badge amber">
            {unavailableMetrics.length} unavailable
          </span>

        </div>


        <div className="customer-unavailable-grid">

          {unavailableMetrics.map(
            (
              [
                key,
                metric,
              ]
            ) => {

              const item =
                metric as {
                  metric?: string
                  status?: string
                  value?: unknown
                  reason?: string
                  required_data?: string[]
                }


              const icon =
                key === 'repeat_purchase'
                  ? (
                    <Repeat2
                      size={18}
                    />
                  )
                  : key === 'ltv'
                    ? (
                      <WalletCards
                        size={18}
                      />
                    )
                    : (
                      <AlertTriangle
                        size={18}
                      />
                    )


              return (
                <div
                  className="customer-unavailable-item"
                  key={key}
                >

                  <div className="customer-unavailable-top">

                    <div className="customer-unavailable-icon">
                      {icon}
                    </div>

                    <div>
                      <strong>
                        {humanizeMetric(
                          item.metric
                          || key
                        )}
                      </strong>

                      <span>
                        {humanizeMetric(
                          item.status
                          || 'unavailable'
                        )}
                      </span>
                    </div>

                  </div>


                  <p>
                    {
                      item.reason
                      || (
                        'Additional customer data '
                        + 'is required.'
                      )
                    }
                  </p>


                  {
                    item.required_data
                      && item.required_data.length > 0
                      && (
                        <div className="required-data-list">

                          <span>
                            Required data
                          </span>

                          <div>
                            {
                              item.required_data.map(
                                (field) => (
                                  <code
                                    key={field}
                                  >
                                    {field}
                                  </code>
                                )
                              )
                            }
                          </div>

                        </div>
                      )
                  }

                </div>
              )
            }
          )}

        </div>

      </div>


      <div className="customer-principle">

        <CheckCircle2
          size={18}
        />

        <p>
          ProfitLens principle: an unavailable metric is
          better than a fabricated metric. Retention, CAC,
          LTV and repeat purchase will only appear once the
          underlying data supports those calculations.
        </p>

      </div>

    </div>
  )
}
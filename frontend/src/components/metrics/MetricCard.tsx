import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  CircleHelp,
} from 'lucide-react'

import type {
  MetricContract,
} from '../../types/metric'


type MetricCardProps = {
  metric: MetricContract

  onClick?: (
    metric: MetricContract
  ) => void

  compact?: boolean
}


function directionIcon(
  direction:
    MetricContract[
      'comparison'
    ]['direction']
) {
  if (direction === 'up') {
    return (
      <ArrowUpRight
        size={14}
      />
    )
  }

  if (direction === 'down') {
    return (
      <ArrowDownRight
        size={14}
      />
    )
  }

  return (
    <ArrowRight
      size={14}
    />
  )
}


export function MetricCard({
  metric,
  onClick,
  compact = false,
}: MetricCardProps) {
  const change =
    metric
      .comparison
      .change_percent

  const clickable =
    Boolean(
      onClick
    )


  return (
    <button
      type="button"
      className={
        [
          'pl-metric-card',

          compact
            ? 'compact'
            : '',

          clickable
            ? 'clickable'
            : '',

          `sentiment-${metric.sentiment}`,
        ]
          .filter(
            Boolean
          )
          .join(' ')
      }
      onClick={
        clickable
          ? () =>
              onClick?.(
                metric
              )
          : undefined
      }
      disabled={
        !clickable
      }
    >

      <div className="pl-metric-card-top">

        <div className="pl-metric-label">
          {metric.label}
        </div>

        {
          metric.definition
          && (
            <CircleHelp
              size={14}
              className="pl-metric-help"
            />
          )
        }

      </div>


      <div className="pl-metric-value">
        {
          metric.formatted_value
          ?? (
            metric.value
            ?? '—'
          )
        }
      </div>


      <div className="pl-metric-footer">

        {
          change !== null
          && change !== undefined
            ? (
              <div
                className={
                  `pl-metric-change ${
                    metric.sentiment
                  }`
                }
              >

                {
                  directionIcon(
                    metric
                      .comparison
                      .direction
                  )
                }

                <span>
                  {
                    change > 0
                      ? '+'
                      : ''
                  }

                  {
                    change.toFixed(
                      2
                    )
                  }%
                </span>

              </div>
            )
            : (
              <div className="pl-metric-change unknown">
                No comparison
              </div>
            )
        }


        <div className="pl-metric-quality">
          {
            metric.data_quality
          }
        </div>

      </div>

    </button>
  )
}

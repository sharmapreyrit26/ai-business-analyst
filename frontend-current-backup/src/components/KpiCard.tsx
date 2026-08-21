import type { ReactNode } from 'react'
import { fmtPct } from '../utils'

export function KpiCard({
  label,
  value,
  change,
  note,
  icon,
}: {
  label: string
  value: string
  change?: number | null
  note?: string
  icon?: ReactNode
}) {
  const changeClass =
    change === null || change === undefined
      ? ''
      : change >= 0
        ? 'positive-text'
        : 'negative-text'

  return (
    <div className="card kpi-card">
      <div className="kpi-top">
        <span>{label}</span>
        <div className="icon-box">{icon}</div>
      </div>
      <strong>{value}</strong>
      <div className="kpi-foot">
        {change !== null && change !== undefined && (
          <span className={changeClass}>{fmtPct(change)}</span>
        )}
        {note && <span>{note}</span>}
      </div>
    </div>
  )
}

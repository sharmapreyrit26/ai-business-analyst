import type { ReactNode } from 'react'

export function KpiCard({ label, value, change, icon, note }: { label: string; value: string; change?: number | null; icon?: ReactNode; note?: string }) {
  const positive = (change ?? 0) >= 0
  return (
    <div className="card kpi-card">
      <div className="kpi-top"><span>{label}</span><div className="icon-chip">{icon}</div></div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-foot">
        {change !== undefined && change !== null ? <span className={`delta ${positive ? 'pos' : 'neg'}`}>{positive ? '▲' : '▼'} {Math.abs(change).toFixed(2)}%</span> : null}
        {note ? <span className="muted">{note}</span> : null}
      </div>
    </div>
  )
}

import { Activity, AlertTriangle, CalendarDays } from 'lucide-react'

export function Header({
  month,
  months,
  partialMonths,
  onMonthChange,
  periodsLoading = false,
  backendConnected = true,
}: {
  month: string
  months: string[]
  partialMonths: string[]
  onMonthChange: (month: string) => void
  periodsLoading?: boolean
  backendConnected?: boolean
}) {
  const isPartialMonth = partialMonths.includes(month)

  return (
    <header className="topbar">
      <div>
        <div className="eyebrow">D2C analytics workspace</div>
        <h1>ProfitLens</h1>
      </div>

      <div className="topbar-actions">
        <div className={`status-pill ${backendConnected ? '' : 'error'}`}>
          <Activity size={14} />
          {backendConnected ? 'Backend connected' : 'Backend unavailable'}
        </div>

        {isPartialMonth && (
          <div className="status-pill warning">
            <AlertTriangle size={14} />
            Partial period
          </div>
        )}

        <div className="month-selector">
          <CalendarDays size={14} />
          <select
            className="select"
            value={month}
            disabled={periodsLoading || months.length === 0}
            onChange={(event) => onMonthChange(event.target.value)}
          >
            {months.map((reportingMonth) => (
              <option key={reportingMonth} value={reportingMonth}>
                {partialMonths.includes(reportingMonth)
                  ? `${reportingMonth} (partial)`
                  : reportingMonth}
              </option>
            ))}
          </select>
        </div>
      </div>
    </header>
  )
}

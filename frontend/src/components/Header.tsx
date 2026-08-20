import { Activity } from 'lucide-react'

export function Header({ month, onMonthChange }: { month: string; onMonthChange: (month: string) => void }) {
  return (
    <header className="topbar">
      <div>
        <div className="eyebrow">D2C analytics workspace</div>
        <h1>ProfitLens</h1>
      </div>
      <div className="topbar-actions">
        <div className="status-pill"><Activity size={14} /> Backend connected</div>
        <select className="select" value={month} onChange={(e) => onMonthChange(e.target.value)}>
          {['2018-08','2018-07','2018-06','2018-05','2018-04','2018-03'].map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>
    </header>
  )
}

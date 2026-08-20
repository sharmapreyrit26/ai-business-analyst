export const fmtNumber = (value?: number | null, digits = 0) => value == null ? '—' : value.toLocaleString('en-IN', { maximumFractionDigits: digits })
export const fmtMoney = (value?: number | null) => {
  if (value == null) return '—'
  const abs = Math.abs(value)
  if (abs >= 10_000_000) return `${value < 0 ? '-' : ''}₹${(abs / 10_000_000).toFixed(2)}Cr`
  if (abs >= 100_000) return `${value < 0 ? '-' : ''}₹${(abs / 100_000).toFixed(2)}L`
  if (abs >= 1_000) return `${value < 0 ? '-' : ''}₹${(abs / 1_000).toFixed(1)}K`
  return `${value < 0 ? '-' : ''}₹${abs.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
}
export const fmtPct = (value?: number | null) => value == null ? '—' : `${value.toFixed(2)}%`

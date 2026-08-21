export function fmtMoney(value?: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value)
}

export function fmtNumber(value?: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(value)
}

export function fmtPct(value?: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return `${Number(value).toFixed(2)}%`
}

export function humanizeMetric(value?: string | null): string {
  if (!value) return 'Not available'
  return value
    .replace(/\\_/g, '_')
    .replace(/_/g, ' ')
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

import type {
  BusinessAnswerResponse,
  CustomerAnalyticsResponse,
  DashboardResponse,
  LogisticsAnalyticsResponse,
  ProductAnalyticsResponse,
  ReportingPeriodsResponse,
  ScenarioResponse,
} from '../types/api'

const configuredBase = import.meta.env.VITE_API_BASE_URL?.trim()
const API_BASE = configuredBase || '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), 25000)

  try {
    const headers = new Headers(init?.headers)

    if (init?.body && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json')
    }

    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers,
      signal: controller.signal,
    })

    if (!response.ok) {
      let detail = `${response.status} ${response.statusText}`
      try {
        const body = await response.json()
        detail = body?.detail || JSON.stringify(body)
      } catch {
        // Keep default HTTP error.
      }
      throw new Error(detail)
    }

    return (await response.json()) as T
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('The request took too long. Please try again.')
    }
    throw error
  } finally {
    window.clearTimeout(timeoutId)
  }
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  reportingPeriods: () =>
    request<ReportingPeriodsResponse>('/analytics/reporting-periods'),
  dashboard: (month: string) =>
    request<DashboardResponse>(`/dashboard/${month}`),
  products: (month: string) =>
    request<ProductAnalyticsResponse>(`/analytics/products/${month}`),
  customers: () =>
    request<CustomerAnalyticsResponse>('/analytics/customers'),
  logistics: (month: string) =>
    request<LogisticsAnalyticsResponse>(`/analytics/logistics/${month}`),
  ask: (question: string, month: string) =>
    request<BusinessAnswerResponse>('/analytics/business-question', {
      method: 'POST',
      body: JSON.stringify({ question, month }),
    }),
  scenario: (question: string, month: string) =>
    request<ScenarioResponse>('/analytics/scenario', {
      method: 'POST',
      body: JSON.stringify({ question, month }),
    }),
}

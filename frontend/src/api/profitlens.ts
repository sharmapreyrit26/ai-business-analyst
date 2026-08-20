import type {
  BusinessAnswerResponse,
  CustomerAnalyticsResponse,
  DashboardResponse,
  LogisticsAnalyticsResponse,
  ProductAnalyticsResponse,
  ScenarioResponse,
} from '../types/api'

const configuredBase = import.meta.env.VITE_API_BASE_URL?.trim()
const API_BASE = configuredBase || '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    ...init,
  })

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`
    try {
      const body = await response.json()
      detail = body?.detail || JSON.stringify(body)
    } catch {
      // use default detail
    }
    throw new Error(detail)
  }

  return response.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  dashboard: (month: string) => request<DashboardResponse>(`/dashboard/${month}`),
  products: (month: string) => request<ProductAnalyticsResponse>(`/analytics/products/${month}`),
  customers: () => request<CustomerAnalyticsResponse>('/analytics/customers'),
  logistics: (month: string) => request<LogisticsAnalyticsResponse>(`/analytics/logistics/${month}`),
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

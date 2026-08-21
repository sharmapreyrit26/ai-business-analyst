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

async function request<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const controller = new AbortController()

  const timeout = setTimeout(
    () => controller.abort(),
    20000
  )

  try {
    const response = await fetch(
      `${API_BASE}${path}`,
      {
        headers: {
          'Content-Type': 'application/json',
          ...(init?.headers || {}),
        },
        ...init,
        signal: controller.signal,
      }
    )

    if (!response.ok) {
      let detail =
        `${response.status} ${response.statusText}`

      try {
        const body = await response.json()

        detail =
          body?.detail ||
          JSON.stringify(body)
      } catch {
        // Keep default error message.
      }

      throw new Error(detail)
    }

    return await response.json() as T

  } catch (error: any) {

    if (error?.name === 'AbortError') {
      throw new Error(
        'ProfitLens analysis took too long. Please try again.'
      )
    }

    throw error

  } finally {
    clearTimeout(timeout)
  }
}
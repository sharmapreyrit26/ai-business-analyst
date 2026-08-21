import type {
  BusinessAnswerResponse,
  D2CAcquisitionChannelsResponse,
  D2CCategoriesResponse,
  D2CCouriersResponse,
  D2CCustomerCohortsResponse,
  D2CCustomerSummaryResponse,
  D2CLogisticsSummaryResponse,
  D2CMarketingCampaignsResponse,
  D2CMarketingChannelsResponse,
  D2CMarketingInsightsResponse,
  D2CMarketingSummaryResponse,
  D2CMarketingTrendResponse,
  D2COverviewResponse,
  D2CPaymentLogisticsResponse,
  D2CProductsResponse,
  D2CZonesResponse,
  ReportingPeriodsResponse,
  ScenarioResponse,
  D2CInventoryCategoriesResponse,
  D2CInventorySkusResponse,
  D2CInventorySummaryResponse,
  D2CInventoryWarehousesResponse,
} from '../types/api'


const configuredBase =
  import.meta.env.VITE_API_BASE_URL?.trim()

const API_BASE =
  configuredBase || '/api'


async function request<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const controller =
    new AbortController()

  const timeoutId =
    window.setTimeout(
      () => controller.abort(),
      25000
    )

  try {
    const headers =
      new Headers(
        init?.headers
      )

    if (
      init?.body
      && !headers.has(
        'Content-Type'
      )
    ) {
      headers.set(
        'Content-Type',
        'application/json'
      )
    }

    const response =
      await fetch(
        `${API_BASE}${path}`,
        {
          ...init,
          headers,
          signal: controller.signal,
        }
      )

    if (!response.ok) {
      let detail =
        `${response.status} ${response.statusText}`

      try {
        const body =
          await response.json()

        detail =
          body?.detail
          || JSON.stringify(body)

      } catch {
        // Keep default HTTP error.
      }

      throw new Error(
        detail
      )
    }

    return (
      await response.json()
    ) as T

  } catch (error) {
    if (
      error instanceof DOMException
      && error.name === 'AbortError'
    ) {
      throw new Error(
        'ProfitLens request took too long. Please try again.'
      )
    }

    throw error

  } finally {
    window.clearTimeout(
      timeoutId
    )
  }
}


/*
|--------------------------------------------------------------------------
| ProfitLens API
|--------------------------------------------------------------------------
*/

export const api = {

  /*
  |--------------------------------------------------------------------------
  | Reporting
  |--------------------------------------------------------------------------
  */

  reportingPeriods: () =>
    request<ReportingPeriodsResponse>(
      '/analytics/d2c/reporting-periods'
    ),


  /*
  |--------------------------------------------------------------------------
  | Executive Overview
  |--------------------------------------------------------------------------
  */

  overview: (
    month: string
  ) =>
    request<D2COverviewResponse>(
      `/analytics/d2c/overview/${month}`
    ),


  /*
  |--------------------------------------------------------------------------
  | Products
  |--------------------------------------------------------------------------
  */

  products: (
    month: string
  ) =>
    request<D2CProductsResponse>(
      `/analytics/d2c/products/${month}`
    ),

  categories: (
    month: string
  ) =>
    request<D2CCategoriesResponse>(
      `/analytics/d2c/categories/${month}`
    ),


  /*
  |--------------------------------------------------------------------------
  | Customers
  |--------------------------------------------------------------------------
  */

  customers: (
    month: string
  ) =>
    request<D2CCustomerSummaryResponse>(
      `/analytics/d2c/customers/${month}`
    ),

  acquisitionChannels: (
    month: string
  ) =>
    request<D2CAcquisitionChannelsResponse>(
      `/analytics/d2c/acquisition-channels/${month}`
    ),

  customerCohorts: () =>
    request<D2CCustomerCohortsResponse>(
      '/analytics/d2c/customer-cohorts'
    ),


  /*
  |--------------------------------------------------------------------------
  | Logistics
  |--------------------------------------------------------------------------
  */

  logistics: (
    month: string
  ) =>
    request<D2CLogisticsSummaryResponse>(
      `/analytics/d2c/logistics/${month}`
    ),

  couriers: (
    month: string
  ) =>
    request<D2CCouriersResponse>(
      `/analytics/d2c/couriers/${month}`
    ),

  paymentLogistics: (
    month: string
  ) =>
    request<D2CPaymentLogisticsResponse>(
      `/analytics/d2c/payment-logistics/${month}`
    ),

  zones: (
    month: string
  ) =>
    request<D2CZonesResponse>(
      `/analytics/d2c/zones/${month}`
    ),

  

  /*
  |--------------------------------------------------------------------------
  | Inventory
  |--------------------------------------------------------------------------
  */

  inventorySummary: () =>
    request<D2CInventorySummaryResponse>(
      '/analytics/d2c/inventory/summary'
    ),

  inventorySkus: () =>
    request<D2CInventorySkusResponse>(
      '/analytics/d2c/inventory/skus'
    ),

  inventoryWarehouses: () =>
    request<D2CInventoryWarehousesResponse>(
      '/analytics/d2c/inventory/warehouses'
    ),

  inventoryCategories: () =>
    request<D2CInventoryCategoriesResponse>(
      '/analytics/d2c/inventory/categories'
    ),
  /*
  |--------------------------------------------------------------------------
  | Marketing
  |--------------------------------------------------------------------------
  */

  marketing: (
    month: string
  ) =>
    request<D2CMarketingSummaryResponse>(
      `/analytics/d2c/marketing/${month}`
    ),

  marketingChannels: (
    month: string
  ) =>
    request<D2CMarketingChannelsResponse>(
      `/analytics/d2c/marketing/channels/${month}`
    ),

  marketingCampaigns: (
    month: string
  ) =>
    request<D2CMarketingCampaignsResponse>(
      `/analytics/d2c/marketing/campaigns/${month}`
    ),

  marketingTrend: () =>
    request<D2CMarketingTrendResponse>(
      '/analytics/d2c/marketing/monthly-trend'
    ),

  marketingInsights: (
    month: string
  ) =>
    request<D2CMarketingInsightsResponse>(
      `/analytics/d2c/marketing/insights/${month}`
    ),


  /*
  |--------------------------------------------------------------------------
  | AI Business Analyst
  |--------------------------------------------------------------------------
  */

  ask: (
    question: string,
    month: string
  ) =>
    request<BusinessAnswerResponse>(
      '/analytics/business-question',
      {
        method: 'POST',

        body: JSON.stringify({
          question,
          month,
        }),
      }
    ),


  /*
  |--------------------------------------------------------------------------
  | Scenario Engine
  |--------------------------------------------------------------------------
  */

  scenario: (
    question: string,
    month: string
  ) =>
    request<ScenarioResponse>(
      '/analytics/scenario',
      {
        method: 'POST',

        body: JSON.stringify({
          question,
          month,
        }),
      }
    ),
}
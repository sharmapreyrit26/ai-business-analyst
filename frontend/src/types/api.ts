export type ReportingPeriodsResponse = {
  months: string[]
  complete_months: string[]
  partial_months: string[]
  default_month: string | null
}


/*
|--------------------------------------------------------------------------
| D2C Executive Overview
|--------------------------------------------------------------------------
*/

export type D2COverviewResponse = {
  month: string

  reporting: {
    inventory_scope: string
    historical_inventory_available: boolean
  }

  revenue: {
    orders: number
    gross_product_revenue: number
    net_product_revenue: number
    realized_revenue: number
    aov: number
    revenue_growth_percent: number
    order_growth_percent: number
  }

  profitability: {
    gross_profit: number
    gross_margin_percent: number
    contribution_profit_before_marketing: number
    contribution_margin_before_marketing_percent: number
    marketing_spend: number
    contribution_profit_after_marketing: number
    contribution_margin_after_marketing_percent: number
    profit_after_marketing_growth_percent: number
  }

  marketing: {
    marketing_spend: number
    attributed_revenue: number
    roas: number
    cac: number
    attributed_orders: number
    new_customers: number
    cost_per_attributed_order: number
    session_conversion_percent: number
    marketing_spend_percent_of_revenue: number
    attribution_level: string
  }

  customers: {
    active_customers: number
    new_customers: number
    repeat_customers: number
    repeat_customer_rate_percent: number
    orders_per_customer: number
    cod_share_percent: number
  }

  logistics: {
    delivery_rate_percent: number
    rto_orders: number
    rto_rate_percent: number
    return_rate_percent: number
    ndr_rate_percent: number
    average_delivery_tat_days: number
    p90_delivery_tat_days: number
    on_time_delivery_percent: number
  }

  products: {
    total_products: number
    loss_making_products: number
    top_5_revenue_share_percent: number
    top_10_revenue_share_percent: number
    profitability_level: string
  }

  inventory: {
    total_skus: number
    warehouses: number
    total_closing_stock_units: number
    inventory_cost_value: number
    below_reorder_rows: number
    out_of_stock_rows: number
    overstock_rows: number
    slow_moving_rows: number
    potential_revenue_at_risk: number
    estimated_trapped_inventory_cost: number
  }

  limitations: {
    marketing_attribution_level: string
    order_level_marketing_allocation_available: boolean
    sku_contribution_profit_available: boolean
    historical_inventory_available: boolean
  }
}


/*
|--------------------------------------------------------------------------
| D2C Products
|--------------------------------------------------------------------------
*/

export type D2CProductRow = {
  sku_id: string
  product_name: string
  category: string
  orders: number
  units_sold: number
  gross_revenue: number
  discounts: number
  net_revenue: number
  cogs: number
  rto_orders: number
  returned_orders: number
  gross_profit: number
  gross_margin_percent: number
  revenue_share_percent: number
  average_selling_price: number
  rto_rate_percent: number
  return_rate_percent: number
}

export type D2CProductsResponse = {
  month: string

  summary: {
    month: string
    total_products: number
    total_net_revenue: number
    total_gross_profit: number
    gross_margin_percent: number
    loss_making_products: number
    top_5_revenue_share_percent: number
    top_10_revenue_share_percent: number
    top_products: D2CProductRow[]
    profitability_level: string
    sku_contribution_profit_available: boolean
    sku_contribution_profit_limitation: string
  }

  products: D2CProductRow[]
}

export type D2CCategoryRow = {
  category: string
  products: number
  orders: number
  units_sold: number
  gross_revenue: number
  discounts: number
  net_revenue: number
  cogs: number
  gross_profit: number
  gross_margin_percent: number
  revenue_share_percent: number
  rto_orders: number
  returned_orders: number
  rto_rate_percent: number
  return_rate_percent: number
}

export type D2CCategoriesResponse = {
  month: string
  categories: D2CCategoryRow[]
}


/*
|--------------------------------------------------------------------------
| D2C Customers
|--------------------------------------------------------------------------
*/

export type D2CCustomerSummaryResponse = {
  month: string
  active_customers: number
  new_customers: number
  repeat_customers: number
  repeat_customer_rate_percent: number
  orders: number
  orders_per_customer: number
  rto_orders: number
  rto_rate_percent: number
  returned_orders: number
  return_rate_percent: number
  cod_orders: number
  cod_share_percent: number
}

export type D2CAcquisitionChannelRow = {
  acquisition_channel: string
  customers: number
  orders: number
  order_value: number
  rto_orders: number
  returned_orders: number
  orders_per_customer: number
  average_order_value: number
  rto_rate_percent: number
  return_rate_percent: number
}

export type D2CAcquisitionChannelsResponse = {
  month: string
  metric_basis: string
  data: D2CAcquisitionChannelRow[]
}

export type D2CCustomerCohortRow = {
  cohort_month: string
  months_since_first_order: number
  cohort_size: number
  active_customers: number
  retention_percent: number
}

export type D2CCustomerCohortsResponse = {
  retention_type: string
  predictive: boolean
  data: D2CCustomerCohortRow[]
}


/*
|--------------------------------------------------------------------------
| Existing Analyst / Scenario Contracts
|--------------------------------------------------------------------------
*/

export type BusinessAnswerResponse = {
  question: string
  month: string
  question_type: string

  analysis_execution?: {
    total_steps: number
    successful_steps: number
    failed_steps: number
  } | null

  ai_available: boolean

  answer: {
    answer: string
    evidence: string[]
    likely_driver: string
    recommended_actions: string[]
  }
}

export type ScenarioResponse = {
  question: string
  month: string
  status: string
  scenario_type?: string | null
  parameters?: Record<string, any> | null
  parser_result?: Record<string, any> | null
  scenario_result?: Record<string, any> | null
}


/*
|--------------------------------------------------------------------------
| Temporary Legacy Logistics Contract
|--------------------------------------------------------------------------
|
| This remains only until the Logistics page is migrated
| to the new D2C logistics endpoints.
|--------------------------------------------------------------------------
*/

export type LogisticsAnalyticsResponse = {
  month?: string | null
  fulfilment_tat: Record<string, any>
  delivery_promise: Record<string, any>
  order_status: Record<string, any>
  data_quality: Record<string, any>
  available_metrics: string[]
  unavailable_metrics: Record<string, any>
}


/*
|--------------------------------------------------------------------------
| Temporary Legacy Customer Contract
|--------------------------------------------------------------------------
|
| This is kept temporarily because the current Customers.tsx
| may still reference it. Once Customers.tsx is replaced with
| the D2C version, this can be removed.
|--------------------------------------------------------------------------
*/

export type CustomerAnalyticsResponse = {
  status: string
  data_quality: Record<string, any>
  available_analysis: Record<string, any>
  unavailable_analysis: Record<string, any>
  next_data_requirement: Record<string, any>
}
export type D2CLogisticsSummaryResponse = {
  month: string

  summary: {
    month: string
    total_orders: number
    delivered_orders: number
    delivery_rate_percent: number
    rto_orders: number
    rto_rate_percent: number
    returned_orders: number
    return_rate_percent: number
    ndr_orders: number
    ndr_rate_percent: number
    cod_orders: number
    cod_share_percent: number
    average_delivery_tat_days: number
    median_delivery_tat_days: number
    p90_delivery_tat_days: number
    average_first_attempt_tat_days: number
    p90_first_attempt_tat_days: number
    promise_measured_orders: number
    on_time_orders: number
    late_orders: number
    on_time_delivery_percent: number
    late_delivery_percent: number
  }

  definitions: Record<string, string>
}

export type D2CCourierRow = {
  courier_name: string
  orders: number
  delivered_orders: number
  delivery_rate_percent: number
  rto_orders: number
  rto_rate_percent: number
  ndr_orders: number
  ndr_rate_percent: number
  average_delivery_tat_days: number
  p90_delivery_tat_days: number
  on_time_delivery_percent: number
  base_shipping_cost: number
  rto_fee: number
}

export type D2CCouriersResponse = {
  month: string
  data: D2CCourierRow[]
}

export type D2CPaymentLogisticsRow = {
  payment_group: string
  orders: number
  rto_orders: number
  rto_rate_percent: number
  ndr_orders: number
  ndr_rate_percent: number
  returned_orders: number
  return_rate_percent: number
  average_delivery_tat_days: number
  p90_delivery_tat_days: number
}

export type D2CPaymentLogisticsResponse = {
  month: string
  data: D2CPaymentLogisticsRow[]
}

export type D2CZoneRow = {
  zone: string
  orders: number
  rto_orders: number
  rto_rate_percent: number
  ndr_orders: number
  ndr_rate_percent: number
  average_delivery_tat_days: number
  p90_delivery_tat_days: number
}

export type D2CZonesResponse = {
  month: string
  data: D2CZoneRow[]
}
export type D2CMarketingSummaryResponse = {
  month: string
  marketing_spend: number
  attributed_revenue: number
  blended_roas: number
  paid_roas: number
  attributed_orders: number
  new_customers: number
  cac: number
  cost_per_order: number
  sessions: number
  clicks: number
  session_conversion_percent: number
  click_through_percent: number
  attribution_level: string
  order_level_attribution_available: boolean
}

export type D2CMarketingChannelRow = {
  channel: string
  spend: number
  attributed_revenue: number
  orders: number
  new_customers: number
  clicks: number
  sessions: number
  roas: number
  cac: number
  cost_per_order: number
  session_conversion_percent: number
  click_through_percent: number
  revenue_per_order: number
  revenue_per_new_customer: number
}

export type D2CMarketingChannelsResponse = {
  month: string
  data: D2CMarketingChannelRow[]
}

export type D2CMarketingCampaignRow = {
  channel: string
  campaign: string
  spend: number
  attributed_revenue: number
  orders: number
  new_customers: number
  clicks: number
  sessions: number
  roas: number
  cac: number
  cost_per_order: number
  session_conversion_percent: number
  click_through_percent: number
  revenue_per_order: number
  revenue_per_new_customer: number
}

export type D2CMarketingCampaignsResponse = {
  month: string
  data: D2CMarketingCampaignRow[]
}

export type D2CMarketingTrendRow = {
  month: string
  spend: number
  attributed_revenue: number
  orders: number
  new_customers: number
  clicks: number
  sessions: number
  roas: number
  cac: number
  cost_per_order: number
  session_conversion_percent: number
  click_through_percent: number
  revenue_per_order: number
  revenue_per_new_customer: number
  spend_growth_percent: number
  revenue_growth_percent: number
  roas_change_percent: number
  cac_change_percent: number
}

export type D2CMarketingTrendResponse = {
  data: D2CMarketingTrendRow[]
}

export type D2CMarketingInsightsResponse = {
  month: string
  best_roas_channel: {
    channel: string
    roas: number
  } | null
  lowest_cac_channel: {
    channel: string
    cac: number
  } | null
  highest_revenue_channel: {
    channel: string
    attributed_revenue: number
  } | null
}
export type D2CInventorySummaryResponse = {
  inventory_scope: string
  historical_inventory_available: boolean
  sku_warehouse_rows: number
  total_skus: number
  warehouses: number
  total_closing_stock_units: number
  inventory_cost_value: number
  inventory_retail_value: number
  below_reorder_rows: number
  low_stock_rows: number
  out_of_stock_rows: number
  overstock_rows: number
  slow_moving_rows: number
  potential_revenue_at_risk: number
  estimated_trapped_inventory_cost: number
  stock_coverage_unit: string
}

export type D2CInventorySkuRow = {
  sku_id: string
  product_name: string
  category: string
  warehouses: number
  opening_stock: number
  closing_stock: number
  units_sold: number
  units_received: number
  reorder_point: number
  inventory_cost_value: number
  inventory_retail_value: number
  potential_revenue_at_risk: number
  estimated_trapped_inventory_cost: number
  below_reorder_locations: number
  low_stock_locations: number
  overstock_locations: number
  slow_moving_locations: number
  stock_to_sales_ratio: number
  is_reorder_candidate: boolean
}

export type D2CInventorySkusResponse = {
  inventory_scope: string
  historical_inventory_available: boolean
  data: D2CInventorySkuRow[]
}

export type D2CInventoryWarehouseRow = {
  warehouse: string
  skus: number
  closing_stock: number
  units_sold: number
  units_received: number
  inventory_cost_value: number
  inventory_retail_value: number
  below_reorder_rows: number
  low_stock_rows: number
  overstock_rows: number
  slow_moving_rows: number
  potential_revenue_at_risk: number
  estimated_trapped_inventory_cost: number
  stock_to_sales_ratio: number
}

export type D2CInventoryWarehousesResponse = {
  inventory_scope: string
  historical_inventory_available: boolean
  data: D2CInventoryWarehouseRow[]
}

export type D2CInventoryCategoryRow = {
  category: string
  skus: number
  closing_stock: number
  units_sold: number
  inventory_cost_value: number
  inventory_retail_value: number
  below_reorder_rows: number
  overstock_rows: number
  potential_revenue_at_risk: number
  estimated_trapped_inventory_cost: number
  stock_to_sales_ratio: number
}

export type D2CInventoryCategoriesResponse = {
  inventory_scope: string
  historical_inventory_available: boolean
  data: D2CInventoryCategoryRow[]
}
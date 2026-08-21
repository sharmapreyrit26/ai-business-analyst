import {
  expect,
  test,
} from '@playwright/test'


const API =
  'http://127.0.0.1:8000'


test(
  'D2C reporting periods are available',
  async ({
    request,
  }) => {
    const response =
      await request.get(
        `${API}/analytics/d2c/reporting-periods`
      )

    expect(
      response.ok()
    ).toBeTruthy()

    const body =
      await response.json()

    expect(
      body.months
    ).toContain(
      '2025-11'
    )

    expect(
      body.default_month
    ).toBeTruthy()
  }
)


test(
  'November overview returns expected D2C metrics',
  async ({
    request,
  }) => {
    const response =
      await request.get(
        `${API}/analytics/d2c/overview/2025-11`
      )

    expect(
      response.ok()
    ).toBeTruthy()

    const body =
      await response.json()

    expect(
      body.month
    ).toBe(
      '2025-11'
    )

    expect(
      body.revenue.orders
    ).toBe(
      9501
    )

    expect(
      body.revenue.realized_revenue
    ).toBeCloseTo(
      11010422,
      0
    )

    expect(
      body.profitability
        .contribution_margin_after_marketing_percent
    ).toBeCloseTo(
      20.73,
      2
    )

    expect(
      body.logistics.rto_rate_percent
    ).toBeCloseTo(
      12.02,
      2
    )

    expect(
      body.customers
        .repeat_customer_rate_percent
    ).toBeCloseTo(
      64.02,
      2
    )
  }
)


test(
  'product endpoint returns real product rows',
  async ({
    request,
  }) => {
    const response =
      await request.get(
        `${API}/analytics/d2c/products/2025-11`
      )

    expect(
      response.ok()
    ).toBeTruthy()

    const body =
      await response.json()

    expect(
      body.products.length
    ).toBeGreaterThan(
      0
    )

    expect(
      body.summary.total_products
    ).toBe(
      250
    )
  }
)


test(
  'customer endpoint reconciles',
  async ({
    request,
  }) => {
    const response =
      await request.get(
        `${API}/analytics/d2c/customers/2025-11`
      )

    expect(
      response.ok()
    ).toBeTruthy()

    const body =
      await response.json()

    expect(
      body.active_customers
    ).toBe(
      8974
    )

    expect(
      body.repeat_customers
    ).toBe(
      5745
    )
  }
)


test(
  'logistics endpoint returns RTO metrics',
  async ({
    request,
  }) => {
    const response =
      await request.get(
        `${API}/analytics/d2c/logistics/2025-11`
      )

    expect(
      response.ok()
    ).toBeTruthy()

    const body =
      await response.json()

    expect(
      body.summary.rto_rate_percent
    ).toBeCloseTo(
      12.02,
      2
    )

    expect(
      body.summary.p90_delivery_tat_days
    ).toBeCloseTo(
      8,
      2
    )
  }
)


test(
  'inventory endpoint reconciles stock',
  async ({
    request,
  }) => {
    const response =
      await request.get(
        `${API}/analytics/d2c/inventory/summary`
      )

    expect(
      response.ok()
    ).toBeTruthy()

    const body =
      await response.json()

    expect(
      body.total_skus
    ).toBe(
      250
    )

    expect(
      body.total_closing_stock_units
    ).toBe(
      510570
    )

    expect(
      body.below_reorder_rows
    ).toBe(
      26
    )
  }
)


test(
  'scenario API calculates combined D2C scenario',
  async ({
    request,
  }) => {
    const response =
      await request.post(
        `${API}/analytics/scenario`,
        {
          data: {
            question:
              'What if orders increase by 10%, AOV increases by 5%, and RTO reduces by 20%?',
            month:
              '2025-11',
          },
        }
      )

    expect(
      response.ok()
    ).toBeTruthy()

    const body =
      await response.json()

    expect(
      body.status
    ).toBe(
      'complete'
    )

    expect(
      body.scenario_type
    ).toBe(
      'd2c_combined_change'
    )

    expect(
      body.parameters
        .order_change_percent
    ).toBe(
      10
    )

    expect(
      body.parameters
        .aov_change_percent
    ).toBe(
      5
    )

    expect(
      body.parameters
        .rto_reduction_percent
    ).toBe(
      20
    )

    expect(
      body.scenario_result
        .difference
        .incremental_revenue
    ).toBeCloseTo(
      2034568.25,
      2
    )
  }
)

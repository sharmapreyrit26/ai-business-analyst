import {
  expect,
  test,
} from '@playwright/test'


test(
  'ProfitLens V2 platform is available',
  async ({
    request,
  }) => {
    const response =
      await request.get(
        'http://127.0.0.1:8000/analytics/v2/health'
      )

    expect(
      response.ok()
    ).toBeTruthy()

    const body =
      await response.json()

    expect(
      body.version
    ).toBe(
      'v2'
    )

    expect(
      body.architecture
    ).toBe(
      'deterministic-first'
    )
  }
)


test(
  'ProfitLens V2 capabilities are available',
  async ({
    request,
  }) => {
    const response =
      await request.get(
        'http://127.0.0.1:8000/analytics/v2/capabilities'
      )

    expect(
      response.ok()
    ).toBeTruthy()

    const body =
      await response.json()

    expect(
      body.scenario_v2
    ).toBeTruthy()

    expect(
      body.investigations
    ).toBeTruthy()

    expect(
      body.alerts
    ).toBeTruthy()

    expect(
      body.metric_dictionary
    ).toBeTruthy()
  }
)

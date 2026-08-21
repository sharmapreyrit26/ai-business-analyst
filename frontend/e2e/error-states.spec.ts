import {
  expect,
  test,
} from '@playwright/test'


test(
  'Overview shows a clean error state when API fails',
  async ({
    page,
  }) => {
    await page.route(
      '**/analytics/d2c/overview/2025-11',
      async route => {
        await route.fulfill({
          status: 500,
          contentType:
            'application/json',
          body: JSON.stringify({
            detail:
              'Simulated overview failure',
          }),
        })
      }
    )

    await page.goto('/')

    await expect(
      page.locator('body')
    ).toContainText(
      /Could not load data/i
    )

    await expect(
      page.locator('body')
    ).not.toContainText(
      /undefined|NaN|\[object Object\]/
    )
  }
)


test(
  'Products shows a clean error state when API fails',
  async ({
    page,
  }) => {
    await page.route(
      '**/analytics/d2c/products/2025-11',
      async route => {
        await route.fulfill({
          status: 500,
          contentType:
            'application/json',
          body: JSON.stringify({
            detail:
              'Simulated products failure',
          }),
        })
      }
    )

    await page.goto(
      '/products'
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /Could not load|error/i
    )
  }
)


test(
  'Marketing handles one failed endpoint without crashing',
  async ({
    page,
  }) => {
    await page.route(
      '**/analytics/d2c/marketing/insights/2025-11',
      async route => {
        await route.fulfill({
          status: 500,
          contentType:
            'application/json',
          body: JSON.stringify({
            detail:
              'Simulated marketing insight failure',
          }),
        })
      }
    )

    await page.goto(
      '/marketing'
    )

    await expect(
      page.locator('body')
    ).toBeVisible()

    const text =
      await page
        .locator('body')
        .innerText()

    expect(
      text
    ).not.toContain(
      'undefined'
    )

    expect(
      text
    ).not.toContain(
      'NaN'
    )
  }
)


test(
  'Inventory shows a clean state when summary API fails',
  async ({
    page,
  }) => {
    await page.route(
      '**/analytics/d2c/inventory/summary',
      async route => {
        await route.fulfill({
          status: 500,
          contentType:
            'application/json',
          body: JSON.stringify({
            detail:
              'Simulated inventory failure',
          }),
        })
      }
    )

    await page.goto(
      '/inventory'
    )

    await expect(
      page.locator('body')
    ).toBeVisible()

    const text =
      await page
        .locator('body')
        .innerText()

    expect(
      text
    ).not.toContain(
      'undefined'
    )

    expect(
      text
    ).not.toContain(
      '[object Object]'
    )
  }
)


test(
  'Ask ProfitLens shows an error card when analyst request fails',
  async ({
    page,
  }) => {
    await page.route(
      '**/analytics/business-question',
      async route => {
        await route.fulfill({
          status: 500,
          contentType:
            'application/json',
          body: JSON.stringify({
            detail:
              'Simulated analyst failure',
          }),
        })
      }
    )

    await page.goto(
      '/analyst'
    )

    await page
      .getByPlaceholder(
        'Ask a business question...'
      )
      .fill(
        'Why did revenue decline?'
      )

    await page
      .getByRole(
        'button',
        {
          name:
            'Ask ProfitLens',
        }
      )
      .click()

    await expect(
      page.getByText(
        'Could not complete analysis'
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.analyst-main-answer'
      )
    ).toHaveCount(
      0
    )
  }
)


test(
  'Scenario Lab shows an error instead of crashing when API fails',
  async ({
    page,
  }) => {
    await page.route(
      '**/analytics/scenario',
      async route => {
        await route.fulfill({
          status: 500,
          contentType:
            'application/json',
          body: JSON.stringify({
            detail:
              'Simulated scenario failure',
          }),
        })
      }
    )

    await page.goto(
      '/scenario'
    )

    await page
      .getByPlaceholder(
        /What if|Example/i
      )
      .first()
      .fill(
        'What if AOV increases by 10%?'
      )

    await page
      .getByRole(
        'button',
        {
          name:
            /Run Scenario/i,
        }
      )
      .click()

    await expect(
      page.locator(
        '.notice.error'
      )
    ).toBeVisible()

    await expect(
      page.locator('body')
    ).not.toContainText(
      /undefined|NaN|\[object Object\]/
    )
  }
)


test(
  'reporting-period failure does not crash the application',
  async ({
    page,
  }) => {
    await page.route(
      '**/analytics/d2c/reporting-periods',
      async route => {
        await route.fulfill({
          status: 500,
          contentType:
            'application/json',
          body: JSON.stringify({
            detail:
              'Simulated reporting period failure',
          }),
        })
      }
    )

    await page.goto('/')

    await expect(
      page.getByRole(
        'heading',
        {
          name: 'ProfitLens',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator('body')
    ).not.toContainText(
      /undefined|NaN|\[object Object\]/
    )
  }
)

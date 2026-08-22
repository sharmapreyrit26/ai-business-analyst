import {
  expect,
  test,
} from '@playwright/test'


test(
  'sidebar navigation works across ProfitLens',
  async ({
    page,
  }) => {
    await page.goto('/')

    const destinations = [
      {
        label:
          'Product Analysis',
        path:
          '/products',
      },
      {
        label:
          'Customer Analysis',
        path:
          '/customers',
      },
      {
        label:
          'Logistics',
        path:
          '/logistics',
      },
      {
        label:
          'Marketing',
        path:
          '/marketing',
      },
      {
        label:
          'Inventory',
        path:
          '/inventory',
      },
      {
        label:
          'Ask ProfitLens',
        path:
          '/analyst',
      },
      {
        label:
          'Scenario Lab',
        path:
          '/scenario',
      },
    ]

    for (
      const destination
      of destinations
    ) {
      await page
        .getByRole(
          'link',
          {
            name:
              destination.label,
          }
        )
        .click()

      await expect(
        page
      ).toHaveURL(
        new RegExp(
          `${destination.path}$`
        )
      )
    }
  }
)


test(
  'marketing page exposes ROAS and CAC',
  async ({
    page,
  }) => {
    await page.goto(
      '/marketing'
    )

    await expect(
      page.getByText(
        /ROAS/i
      ).first()
    ).toBeVisible()

    await expect(
      page.getByText(
        /CAC/i
      ).first()
    ).toBeVisible()
  }
)


test(
  'logistics page exposes RTO metrics',
  async ({
    page,
  }) => {
    await page.goto(
      '/logistics'
    )

    await expect(
      page.getByText(
        /RTO/i
      ).first()
    ).toBeVisible()

    await expect(
      page.locator(
        'body'
      )
    ).toContainText(
      '12.02'
    )
  }
)


test(
  'inventory page exposes stock risks',
  async ({
    page,
  }) => {
    await page.goto(
      '/inventory'
    )

    const body =
      page.locator(
        'body'
      )

    await expect(
      body
    ).toContainText(
      /reorder/i
    )

    await expect(
      body
    ).toContainText(
      /overstock/i
    )
  }
)


test(
  'Scenario Lab runs an AOV scenario',
  async ({
    page,
  }) => {
    await page.goto(
      '/scenario'
    )

    const aovControl =
      page
        .locator(
          '.pl-scenario-control'
        )
        .filter({
          hasText:
            /AOV|Average Order Value/i,
        })

    await aovControl
      .locator(
        'input[type="number"]'
      )
      .fill(
        '10'
      )

    await page
      .getByRole(
        'button',
        {
          name:
            /Run scenario/i,
        }
      )
      .click()

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Scenario result',
        }
      )
    ).toBeVisible({
      timeout: 10000,
    })

    await expect(
      page.locator(
        '.pl-scenario-result-card'
      ).first()
    ).toBeVisible()
  }
)


test(
  'Scenario Lab runs RTO reduction',
  async ({
    page,
  }) => {
    await page.goto(
      '/scenario'
    )

    const rtoControl =
      page
        .locator(
          '.pl-scenario-control'
        )
        .filter({
          hasText:
            /RTO/i,
        })

    await rtoControl
      .locator(
        'input[type="number"]'
      )
      .fill(
        '20'
      )

    await page
      .getByRole(
        'button',
        {
          name:
            /Run scenario/i,
        }
      )
      .click()

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Scenario result',
        }
      )
    ).toBeVisible({
      timeout: 10000,
    })
  }
)


test(
  'Scenario Lab runs combined scenario',
  async ({
    page,
  }) => {
    await page.goto(
      '/scenario'
    )

    const controls =
      page.locator(
        '.pl-scenario-control'
      )

    await controls
      .filter({
        hasText:
          /Orders/i,
      })
      .locator(
        'input[type="number"]'
      )
      .fill(
        '10'
      )

    await controls
      .filter({
        hasText:
          /AOV|Average Order Value/i,
      })
      .locator(
        'input[type="number"]'
      )
      .fill(
        '5'
      )

    await controls
      .filter({
        hasText:
          /RTO/i,
      })
      .locator(
        'input[type="number"]'
      )
      .fill(
        '20'
      )

    await page
      .getByRole(
        'button',
        {
          name:
            /Run scenario/i,
        }
      )
      .click()

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Scenario result',
        }
      )
    ).toBeVisible({
      timeout: 10000,
    })

    await expect(
      page.locator(
        '.pl-scenario-result-card'
      ).first()
    ).toBeVisible()
  }
)


test(
  'no horizontal overflow at desktop width',
  async ({
    page,
  }) => {
    const routes = [
      '/',
      '/products',
      '/customers',
      '/logistics',
      '/marketing',
      '/inventory',
      '/analyst',
      '/scenario',
    ]

    for (
      const route
      of routes
    ) {
      await page.goto(
        route
      )

      const dimensions =
        await page.evaluate(
          () => ({
            width:
              document.documentElement
                .scrollWidth,

            viewport:
              document.documentElement
                .clientWidth,
          })
        )

      expect(
        dimensions.width
      ).toBeLessThanOrEqual(
        dimensions.viewport + 2
      )
    }
  }
)

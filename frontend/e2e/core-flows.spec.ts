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

    const input =
      page.getByPlaceholder(
        /What if|Example/i
      ).first()

    await input.fill(
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
      page.getByText(
        /Scenario Result/i
      ).first()
    ).toBeVisible()

    await expect(
      page.locator(
        'body'
      )
    ).toContainText(
      /1,275|1275/
    )
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

    const input =
      page.getByPlaceholder(
        /What if|Example/i
      ).first()

    await input.fill(
      'What if RTO reduces by 20%?'
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
        'body'
      )
    ).toContainText(
      '9.62'
    )

    await expect(
      page.locator(
        'body'
      )
    ).toContainText(
      /3,27,953|327953/
    )
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

    const input =
      page.getByPlaceholder(
        /What if|Example/i
      ).first()

    await input.fill(
      'What if orders increase by 10%, AOV increases by 5%, and RTO reduces by 20%?'
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

    const body =
      page.locator(
        'body'
      )

    await expect(
      body
    ).toContainText(
      '9.62'
    )

    await expect(
      body
    ).toContainText(
      /1,30,44,990|13044990/
    )

    await expect(
      body
    ).toContainText(
      /30,19,251|3019251/
    )
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

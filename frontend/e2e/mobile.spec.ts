import {
  expect,
  test,
} from '@playwright/test'


const mobileViewport = {
  width: 390,
  height: 844,
}


const routes = [
  {
    name: 'Overview',
    path: '/',
  },
  {
    name: 'Products',
    path: '/products',
  },
  {
    name: 'Customers',
    path: '/customers',
  },
  {
    name: 'Logistics',
    path: '/logistics',
  },
  {
    name: 'Marketing',
    path: '/marketing',
  },
  {
    name: 'Inventory',
    path: '/inventory',
  },
  {
    name: 'Ask ProfitLens',
    path: '/analyst',
  },
  {
    name: 'Scenario Lab',
    path: '/scenario',
  },
]


for (
  const route
  of routes
) {
  test(
    `${route.name} renders without overflow on mobile`,
    async ({
      page,
    }) => {
      await page.setViewportSize(
        mobileViewport
      )

      await page.goto(
        route.path
      )

      await page.waitForLoadState(
        'networkidle'
      )

      await expect(
        page.locator(
          'body'
        )
      ).toBeVisible()

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
        dimensions.width,
        `${route.name} has horizontal overflow`
      ).toBeLessThanOrEqual(
        dimensions.viewport + 2
      )

      const bodyText =
        await page
          .locator(
            'body'
          )
          .innerText()

      const invalidValues = [
        'undefined',
        'NaN',
        '[object Object]',
        'np.float64',
        'Internal Server Error',
      ]

      for (
        const invalidValue
        of invalidValues
      ) {
        expect(
          bodyText
        ).not.toContain(
          invalidValue
        )
      }
    }
  )
}


test(
  'mobile month selector remains usable',
  async ({
    page,
  }) => {
    await page.setViewportSize(
      mobileViewport
    )

    await page.goto('/')

    const monthSelect =
      page.locator(
        '.month-selector select'
      )

    await expect(
      monthSelect
    ).toBeVisible()

    await expect(
      monthSelect
    ).toBeEnabled()

    await page.waitForLoadState(
      'networkidle'
    )

    await monthSelect.selectOption(
      '2025-10'
    )

    await expect(
      monthSelect
    ).toHaveValue(
      '2025-10'
    )
  }
)


test(
  'Ask ProfitLens is usable on mobile',
  async ({
    page,
  }) => {
    await page.setViewportSize(
      mobileViewport
    )

    await page.goto(
      '/analyst'
    )

    const input =
      page.getByPlaceholder(
        'Ask a business question...'
      )

    await expect(
      input
    ).toBeVisible()

    await input.fill(
      'Why is RTO high?'
    )

    const submitButton =
      page.getByRole(
        'button',
        {
          name:
            'Ask ProfitLens',
        }
      )

    await expect(
      submitButton
    ).toBeVisible()

    await submitButton.click()

    await expect(
      page.locator(
        '.analyst-main-answer'
      )
    ).toBeVisible({
      timeout: 15000,
    })
  }
)


test(
  'Scenario Lab is usable on mobile',
  async ({
    page,
  }) => {
    await page.setViewportSize(
      mobileViewport
    )

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

    const input =
      aovControl.locator(
        'input[type="number"]'
      )

    await expect(
      input
    ).toBeVisible()

    await input.fill(
      '10'
    )

    const runButton =
      page.getByRole(
        'button',
        {
          name:
            /Run scenario/i,
        }
      )

    await expect(
      runButton
    ).toBeVisible()

    await expect(
      runButton
    ).toBeEnabled()

    await runButton.click()

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

    const dimensions =
      await page.evaluate(
        () => ({
          width:
            document
              .documentElement
              .scrollWidth,

          viewport:
            document
              .documentElement
              .clientWidth,
        })
      )

    expect(
      dimensions.width
    ).toBeLessThanOrEqual(
      dimensions.viewport + 2
    )
  }
)


import {
  expect,
  test,
} from '@playwright/test'


test(
  'Revenue and Profit page loads financial metrics',
  async ({
    page,
  }) => {
    await page.goto(
      '/revenue-profit'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Revenue & Profit',
          exact: true,
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-metric-card'
      )
    ).toHaveCount(
      6
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /Realized Revenue/i
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /Contribution Profit/i
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /Gross Margin/i
    )
  }
)


test(
  'Revenue and Profit shows financial trend',
  async ({
    page,
  }) => {
    await page.goto(
      '/revenue-profit'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Revenue trend',
        }
      )
    ).toBeVisible({
      timeout: 10000,
    })

    await expect(
      page.locator(
        '.pl-financial-trend-column'
      ).first()
    ).toBeVisible()
  }
)


test(
  'Revenue and Profit exposes profitability bridge',
  async ({
    page,
  }) => {
    await page.goto(
      '/revenue-profit'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Where profit goes',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-profit-bridge-row'
      )
    ).toHaveCount(
      4
    )

    await expect(
      page.locator(
        '.pl-profit-bridge'
      )
    ).toContainText(
      /Marketing spend/i
    )
  }
)


test(
  'Revenue and Profit is mobile-safe',
  async ({
    page,
  }) => {
    await page.setViewportSize({
      width: 390,
      height: 844,
    })

    await page.goto(
      '/revenue-profit'
    )

    await page.waitForTimeout(
      1800
    )

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

import {
  expect,
  test,
} from '@playwright/test'


test(
  'Business Health V2 is the root dashboard',
  async ({
    page,
  }) => {
    await page.goto('/')

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            /Business Health|ProfitLens/i,
        }
      ).first()
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-business-health'
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-business-health'
      )
    ).toContainText(
      /Revenue|Contribution Profit|Orders|RTO/i,
      {
        timeout: 15000,
      }
    )
  }
)


test(
  'Business Health V2 shows prioritized intelligence',
  async ({
    page,
  }) => {
    await page.goto('/')

    await expect(
      page.locator('body')
    ).toContainText(
      /investigation|priority|alert/i
    )

    await expect(
      page.locator(
        '.pl-business-health'
      )
    ).toBeVisible()
  }
)


test(
  'Business Health V2 preserves selected reporting month',
  async ({
    page,
  }) => {
    await page.goto('/')

    const monthSelect =
      page.locator(
        '.month-selector select'
      )

    await monthSelect
      .selectOption(
        '2025-10'
      )

    await expect(
      monthSelect
    ).toHaveValue(
      '2025-10'
    )

    await page.goto(
      '/revenue-profit'
    )

    await page.goto('/')

    await expect(
      monthSelect
    ).toHaveValue(
      '2025-10'
    )
  }
)


test(
  'Business Health V2 exposes founder actions',
  async ({
    page,
  }) => {
    await page.goto('/')

    await expect(
      page.getByRole(
        'button',
        {
          name:
            /Ask ProfitLens/i,
        }
      )
    ).toBeVisible()

    await expect(
      page.locator('body')
    ).toContainText(
      /scenario|investigate/i
    )
  }
)


test(
  'Business Health V2 is mobile-safe',
  async ({
    page,
  }) => {
    await page.setViewportSize({
      width: 390,
      height: 844,
    })

    await page.goto('/')

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

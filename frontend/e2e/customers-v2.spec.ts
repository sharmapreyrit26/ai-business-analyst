import {
  expect,
  test,
} from '@playwright/test'


test(
  'Customer Analysis V2 loads customer health metrics',
  async ({
    page,
  }) => {
    await page.goto(
      '/customers'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Customer Analysis',
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
      /Repeat Customer Rate/i
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /Orders Per Customer/i
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /Customer RTO Rate/i
    )
  }
)


test(
  'Customer Analysis V2 shows acquisition quality',
  async ({
    page,
  }) => {
    await page.goto(
      '/customers'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Customer volume by channel',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-customer-channel-row'
      ).first()
    ).toBeVisible()

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Lowest fulfillment risk',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-customer-quality-row'
      ).first()
    ).toBeVisible()
  }
)


test(
  'Customer Analysis V2 shows observed cohort retention when available',
  async ({
    page,
  }) => {
    await page.goto(
      '/'
    )

    const monthSelect =
      page.locator(
        '.month-selector select'
      )

    await monthSelect
      .selectOption(
        '2025-08'
      )

    await page.goto(
      '/customers'
    )

    await expect(
      monthSelect
    ).toHaveValue(
      '2025-08'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Cohort retention',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-retention-row'
      ).first()
    ).toBeVisible({
      timeout: 10000,
    })

    await expect(
      page.locator(
        '.pl-customer-scope-note'
      )
    ).toContainText(
      /observed historical behaviour/i
    )
  }
)


test(
  'Customer Analysis V2 shows detailed acquisition table',
  async ({
    page,
  }) => {
    await page.goto(
      '/customers'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Acquisition channel comparison',
        }
      )
    ).toBeVisible()

    const table =
      page.locator(
        '.pl-customers-v2 .data-table'
      )

    await expect(
      table
    ).toBeVisible()

    await expect(
      table
    ).toContainText(
      /Meta/i
    )

    await expect(
      table
    ).toContainText(
      /Organic/i
    )
  }
)


test(
  'Customer Analysis V2 is mobile-safe',
  async ({
    page,
  }) => {
    await page.setViewportSize({
      width: 390,
      height: 844,
    })

    await page.goto(
      '/customers'
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

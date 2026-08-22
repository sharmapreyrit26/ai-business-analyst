import {
  expect,
  test,
} from '@playwright/test'


test(
  'Logistics V2 loads logistics health metrics',
  async ({
    page,
  }) => {
    await page.goto(
      '/logistics'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Logistics Performance',
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
      /RTO Rate/i
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /NDR Rate/i
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /On-Time Delivery/i
    )
  }
)


test(
  'Logistics V2 exposes COD versus prepaid risk',
  async ({
    page,
  }) => {
    await page.goto(
      '/logistics'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'COD vs Prepaid',
        }
      )
    ).toBeVisible()

    const cards =
      page.locator(
        '.pl-payment-risk-card'
      )

    await expect(
      cards
    ).toHaveCount(
      2
    )

    await expect(
      page.locator(
        '.pl-payment-risk-grid'
      )
    ).toContainText(
      /COD/i
    )

    await expect(
      page.locator(
        '.pl-payment-risk-grid'
      )
    ).toContainText(
      /Prepaid/i
    )
  }
)


test(
  'Logistics V2 ranks courier performance',
  async ({
    page,
  }) => {
    await page.goto(
      '/logistics'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Fastest couriers',
        }
      )
    ).toBeVisible()

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Highest RTO couriers',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-courier-row'
      ).first()
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-logistics-v2'
      )
    ).toContainText(
      /Blue Dart/i
    )

    await expect(
      page.locator(
        '.pl-logistics-v2'
      )
    ).toContainText(
      /Xpressbees/i
    )
  }
)


test(
  'Logistics V2 shows zone performance',
  async ({
    page,
  }) => {
    await page.goto(
      '/logistics'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Zone performance',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-zone-row'
      )
    ).toHaveCount(
      5
    )

    await expect(
      page.locator(
        '.pl-zone-list'
      )
    ).toContainText(
      /North/i
    )
  }
)


test(
  'Logistics V2 exposes detailed courier comparison',
  async ({
    page,
  }) => {
    await page.goto(
      '/logistics'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Courier comparison',
        }
      )
    ).toBeVisible()

    const table =
      page.locator(
        '.pl-logistics-v2 .data-table'
      )

    await expect(
      table
    ).toBeVisible()

    await expect(
      table
    ).toContainText(
      /Delivery/i
    )

    await expect(
      table
    ).toContainText(
      /RTO Fee/i
    )
  }
)


test(
  'Logistics V2 is mobile-safe',
  async ({
    page,
  }) => {
    await page.setViewportSize({
      width: 390,
      height: 844,
    })

    await page.goto(
      '/logistics'
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

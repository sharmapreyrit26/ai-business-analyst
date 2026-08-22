import {
  expect,
  test,
} from '@playwright/test'


test(
  'Investigations page loads deterministic business issues',
  async ({
    page,
  }) => {
    await page.goto(
      '/investigations'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Investigations',
          exact: true,
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-investigation-card'
      ).first()
    ).toBeVisible({
      timeout: 10000,
    })

    await expect(
      page.locator('body')
    ).not.toContainText(
      /\b(?:NaN|undefined|null)\b/i
    )
  }
)


test(
  'Investigations page is mobile-safe',
  async ({
    page,
  }) => {
    await page.setViewportSize({
      width: 390,
      height: 844,
    })

    await page.goto(
      '/investigations'
    )

    await page.waitForTimeout(
      1500
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

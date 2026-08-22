import {
  expect,
  test,
} from '@playwright/test'


test(
  'Scenario Lab V2 loads structured controls',
  async ({
    page,
  }) => {
    await page.goto(
      '/scenario'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Scenario Lab',
          exact: true,
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-scenario-control'
      ).first()
    ).toBeVisible({
      timeout: 10000,
    })

    await expect(
      page.getByRole(
        'button',
        {
          name:
            /Run scenario/i,
        }
      )
    ).toBeVisible()
  }
)


test(
  'Scenario Lab V2 runs an orders and AOV scenario',
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

    const ordersControl =
      controls.filter({
        hasText:
          /Orders/i,
      })

    const aovControl =
      controls.filter({
        hasText:
          /AOV|Average Order Value/i,
      })

    await ordersControl
      .locator(
        'input[type="number"]'
      )
      .fill(
        '10'
      )

    await aovControl
      .locator(
        'input[type="number"]'
      )
      .fill(
        '5'
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

    await expect(
      page.locator(
        '.pl-scenario-result-card'
      ).first()
    ).toBeVisible()
  }
)


test(
  'Scenario Lab V2 runs RTO reduction',
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
  'Scenario Lab reset clears scenario state',
  async ({
    page,
  }) => {
    await page.goto(
      '/scenario'
    )

    const ordersControl =
      page
        .locator(
          '.pl-scenario-control'
        )
        .filter({
          hasText:
            /Orders/i,
        })

    const input =
      ordersControl.locator(
        'input[type="number"]'
      )

    await input.fill(
      '15'
    )

    await expect(
      input
    ).toHaveValue(
      '15'
    )

    await page
      .getByRole(
        'button',
        {
          name:
            /Reset/i,
        }
      )
      .click()

    await expect(
      input
    ).toHaveValue(
      '0'
    )
  }
)


test(
  'Scenario Lab V2 preserves selected month',
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
        '2025-10'
      )

    await page.goto(
      '/scenario'
    )

    await expect(
      monthSelect
    ).toHaveValue(
      '2025-10'
    )

    await expect(
      page.locator(
        '.pl-business-hero'
      )
    ).toContainText(
      '2025-10'
    )
  }
)


test(
  'Scenario Lab V2 is mobile-safe',
  async ({
    page,
  }) => {
    await page.setViewportSize({
      width: 390,
      height: 844,
    })

    await page.goto(
      '/scenario'
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

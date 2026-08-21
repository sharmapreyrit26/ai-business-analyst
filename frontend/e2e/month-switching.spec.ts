import {
  expect,
  test,
} from '@playwright/test'


test(
  'selected month updates Overview and persists across pages',
  async ({
    page,
  }) => {
    // --------------------------------------------------
    // INITIAL APP LOAD
    // --------------------------------------------------

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

    // Wait for startup API requests and React
    // initialization to finish before changing month.
    await page.waitForLoadState(
      'networkidle'
    )

    await expect(
      monthSelect
    ).toHaveValue(
      '2025-11'
    )

    await expect(
      monthSelect.locator(
        'option[value="2025-10"]'
      )
    ).toHaveCount(
      1
    )


    // --------------------------------------------------
    // SWITCH OVERVIEW TO OCTOBER
    // --------------------------------------------------

    const overviewRequest =
      page.waitForResponse(
        response =>
          response
            .url()
            .includes(
              '/analytics/d2c/overview/2025-10'
            )
          && response.status()
            === 200
      )

    await monthSelect.selectOption(
      '2025-10'
    )

    await overviewRequest

    await expect(
      monthSelect
    ).toHaveValue(
      '2025-10'
    )


    // --------------------------------------------------
    // NAVIGATE TO PRODUCTS
    // MONTH SHOULD PERSIST
    // --------------------------------------------------

    const productRequest =
      page.waitForResponse(
        response =>
          response
            .url()
            .includes(
              '/analytics/d2c/products/2025-10'
            )
          && response.status()
            === 200
      )

    await page
      .getByRole(
        'link',
        {
          name:
            'Product Analysis',
        }
      )
      .click()

    await productRequest

    await expect(
      page
    ).toHaveURL(
      /\/products$/
    )

    await expect(
      page.locator(
        '.month-selector select'
      )
    ).toHaveValue(
      '2025-10'
    )


    // --------------------------------------------------
    // CHANGE PRODUCTS BACK TO NOVEMBER
    // --------------------------------------------------

    const novemberProductRequest =
      page.waitForResponse(
        response =>
          response
            .url()
            .includes(
              '/analytics/d2c/products/2025-11'
            )
          && response.status()
            === 200
      )

    await page
      .locator(
        '.month-selector select'
      )
      .selectOption(
        '2025-11'
      )

    await novemberProductRequest

    await expect(
      page.locator(
        '.month-selector select'
      )
    ).toHaveValue(
      '2025-11'
    )
  }
)

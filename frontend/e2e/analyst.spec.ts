import {
  expect,
  test,
} from '@playwright/test'


test(
  'Ask ProfitLens answers a revenue question',
  async ({
    page,
  }) => {
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
      'Why did revenue decline in November?'
    )

    await page
      .getByRole(
        'button',
        {
          name:
            'Ask ProfitLens',
        }
      )
      .click()

    await expect(
      page.locator(
        '.analyst-main-answer'
      )
    ).toBeVisible({
      timeout: 15000,
    })

    const body =
      page.locator(
        'body'
      )

    await expect(
      body
    ).toContainText(
      /revenue/i
    )

    await expect(
      body
    ).toContainText(
      /46\.44/
    )

    await expect(
      body
    ).toContainText(
      /Deterministic fallback|AI interpreted/
    )
  }
)


test(
  'Ask ProfitLens answers a marketing question',
  async ({
    page,
  }) => {
    await page.goto(
      '/analyst'
    )

    const input =
      page.getByPlaceholder(
        'Ask a business question...'
      )

    await input.fill(
      'Is our marketing efficient?'
    )

    await page
      .getByRole(
        'button',
        {
          name:
            'Ask ProfitLens',
        }
      )
      .click()

    const answer =
      page.locator(
        '.analyst-main-answer'
      )

    await expect(
      answer
    ).toBeVisible({
      timeout: 15000,
    })

    await expect(
      page.locator(
        'body'
      )
    ).toContainText(
      /ROAS/i
    )

    await expect(
      page.locator(
        'body'
      )
    ).toContainText(
      /5\.32/
    )
  }
)


test(
  'Ask ProfitLens answers a logistics question',
  async ({
    page,
  }) => {
    await page.goto(
      '/analyst'
    )

    const input =
      page.getByPlaceholder(
        'Ask a business question...'
      )

    await input.fill(
      'Why is RTO high?'
    )

    await page
      .getByRole(
        'button',
        {
          name:
            'Ask ProfitLens',
        }
      )
      .click()

    await expect(
      page.locator(
        '.analyst-main-answer'
      )
    ).toBeVisible({
      timeout: 15000,
    })

    const body =
      page.locator(
        'body'
      )

    await expect(
      body
    ).toContainText(
      /RTO/i
    )

    await expect(
      body
    ).toContainText(
      /12\.02/
    )

    await expect(
      body
    ).toContainText(
      /COD/i
    )
  }
)


test(
  'Ask ProfitLens preserves selected reporting month',
  async ({
    page,
  }) => {
    await page.goto(
      '/analyst'
    )

    const monthSelect =
      page.locator(
        '.month-selector select'
      )

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

    const analystRequest =
      page.waitForResponse(
        response =>
          response
            .url()
            .includes(
              '/analytics/business-question'
            )
          && response
            .request()
            .method()
            === 'POST'
          && response.status()
            === 200
      )

    await page
      .getByPlaceholder(
        'Ask a business question...'
      )
      .fill(
        'Why did revenue change?'
      )

    await page
      .getByRole(
        'button',
        {
          name:
            'Ask ProfitLens',
        }
      )
      .click()

    const response =
      await analystRequest

    const body =
      await response.json()

    expect(
      body.month
    ).toBe(
      '2025-10'
    )

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
  'Ask ProfitLens never renders invalid values',
  async ({
    page,
  }) => {
    await page.goto(
      '/analyst'
    )

    await page
      .getByPlaceholder(
        'Ask a business question...'
      )
      .fill(
        'What are the three biggest problems in the business?'
      )

    await page
      .getByRole(
        'button',
        {
          name:
            'Ask ProfitLens',
        }
      )
      .click()

    await expect(
      page.locator(
        '.analyst-main-answer'
      )
    ).toBeVisible({
      timeout: 15000,
    })

    const text =
      await page
        .locator(
          'body'
        )
        .innerText()

    const forbidden = [
      'undefined',
      'NaN',
      '[object Object]',
      'np.float64',
    ]

    for (
      const value
      of forbidden
    ) {
      expect(
        text
      ).not.toContain(
        value
      )
    }
  }
)

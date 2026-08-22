import {
  expect,
  test,
} from '@playwright/test'


test(
  'Product Analysis V2 loads portfolio health metrics',
  async ({
    page,
  }) => {
    await page.goto(
      '/products'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Product Performance',
          exact: true,
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-metric-grid'
      )
    ).toBeVisible()

    await expect(
      page.locator('body')
    ).toContainText(
      /Gross Profit/i
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /Gross Margin/i
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /Loss-Making SKUs/i
    )
  }
)


test(
  'Product Analysis V2 shows revenue and margin leaders',
  async ({
    page,
  }) => {
    await page.goto(
      '/products'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Highest revenue products',
        }
      )
    ).toBeVisible()

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Highest gross-margin products',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-product-ranking-row'
      ).first()
    ).toBeVisible()
  }
)


test(
  'Product Analysis V2 exposes operational risk',
  async ({
    page,
  }) => {
    await page.goto(
      '/products'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Products needing attention',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-product-ranking-row.risk'
      ).first()
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-products-v2'
      )
    ).toContainText(
      /RTO/i
    )

    await expect(
      page.locator(
        '.pl-products-v2'
      )
    ).toContainText(
      /Returns/i
    )
  }
)


test(
  'Product Analysis V2 shows category economics',
  async ({
    page,
  }) => {
    await page.goto(
      '/products'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Revenue and margin by category',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-product-category-row'
      ).first()
    ).toBeVisible()

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Category performance',
        }
      )
    ).toBeVisible()
  }
)


test(
  'Product Analysis V2 search filters SKU explorer',
  async ({
    page,
  }) => {
    await page.goto(
      '/products'
    )

    const search =
      page.getByPlaceholder(
        'Search SKU or product...'
      )

    await search.fill(
      'SKU_174'
    )

    const table =
      page.locator(
        '.pl-products-v2 .data-table'
      ).last()

    await expect(
      table
    ).toContainText(
      'SKU_174'
    )

    await expect(
      table
    ).not.toContainText(
      'SKU_032'
    )
  }
)


test(
  'Product Analysis V2 category filter works',
  async ({
    page,
  }) => {
    await page.goto(
      '/products'
    )

    const category =
      page.getByLabel(
        'Product category'
      )

    await category.selectOption(
      'Footwear'
    )

    const table =
      page.locator(
        '.pl-products-v2 .data-table'
      ).last()

    await expect(
      table
    ).toContainText(
      /Footwear/i
    )

    await expect(
      table
    ).not.toContainText(
      /Skincare/i
    )
  }
)


test(
  'Product Analysis V2 risk filter works',
  async ({
    page,
  }) => {
    await page.goto(
      '/products'
    )

    const risk =
      page.getByLabel(
        'Product risk'
      )

    await risk.selectOption(
      'high-rto'
    )

    await expect(
      risk
    ).toHaveValue(
      'high-rto'
    )

    await expect(
      page.locator(
        '.pl-product-result-count'
      )
    ).toBeVisible()
  }
)


test(
  'Product Analysis V2 states SKU profitability limitation',
  async ({
    page,
  }) => {
    await page.goto(
      '/products'
    )

    const note =
      page.locator(
        '.pl-product-scope-note'
      )

    await expect(
      note
    ).toContainText(
      /gross profit/i
    )

    await expect(
      note
    ).toContainText(
      /Contribution profit is not allocated to individual SKUs/i
    )
  }
)


test(
  'Product Analysis V2 is mobile-safe',
  async ({
    page,
  }) => {
    await page.setViewportSize({
      width: 390,
      height: 844,
    })

    await page.goto(
      '/products'
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

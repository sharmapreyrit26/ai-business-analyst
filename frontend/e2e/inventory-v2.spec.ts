import {
  expect,
  test,
} from '@playwright/test'


test(
  'Inventory V2 loads working capital health metrics',
  async ({
    page,
  }) => {
    await page.goto(
      '/inventory'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Inventory Performance',
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
      /Trapped Inventory Cost/i
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /Revenue At Risk/i
    )

    await expect(
      page.locator('body')
    ).toContainText(
      /Overstock Positions/i
    )
  }
)


test(
  'Inventory V2 shows replenishment and trapped capital priorities',
  async ({
    page,
  }) => {
    await page.goto(
      '/inventory'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Highest revenue-at-risk SKUs',
        }
      )
    ).toBeVisible()

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Highest trapped-capital SKUs',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-inventory-priority-row'
      ).first()
    ).toBeVisible()
  }
)


test(
  'Inventory V2 shows warehouse and category intelligence',
  async ({
    page,
  }) => {
    await page.goto(
      '/inventory'
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Working capital by warehouse',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-inventory-warehouse-row'
      )
    ).toHaveCount(
      3
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'Capital tied up by category',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-inventory-category-row'
      ).first()
    ).toBeVisible()
  }
)


test(
  'Inventory V2 search filters SKU table',
  async ({
    page,
  }) => {
    await page.goto(
      '/inventory'
    )

    const search =
      page.getByPlaceholder(
        'Search SKU or product'
      )

    await search.fill(
      'SKU_094'
    )

    const table =
      page.locator(
        '.pl-inventory-v2 .data-table'
      )

    await expect(
      table
    ).toContainText(
      'SKU_094'
    )

    await expect(
      table
    ).not.toContainText(
      'SKU_002'
    )
  }
)


test(
  'Inventory V2 category filter works',
  async ({
    page,
  }) => {
    await page.goto(
      '/inventory'
    )

    const category =
      page.getByLabel(
        'Inventory category'
      )

    await category.selectOption(
      'Jeans'
    )

    const table =
      page.locator(
        '.pl-inventory-v2 .data-table'
      )

    await expect(
      table
    ).toContainText(
      /Jeans/i
    )

    await expect(
      table
    ).not.toContainText(
      /Skincare/i
    )
  }
)


test(
  'Inventory V2 reorder filter works',
  async ({
    page,
  }) => {
    await page.goto(
      '/inventory'
    )

    const checkbox =
      page.getByRole(
        'checkbox',
        {
          name:
            /Reorder candidates only/i,
        }
      )

    await checkbox.check()

    await expect(
      checkbox
    ).toBeChecked()

    await expect(
      page.locator(
        '.pl-inventory-result-count'
      )
    ).toBeVisible()
  }
)


test(
  'Inventory V2 states snapshot limitation',
  async ({
    page,
  }) => {
    await page.goto(
      '/inventory'
    )

    await expect(
      page.locator(
        '.pl-inventory-scope-note'
      )
    ).toContainText(
      /current stock snapshot/i
    )

    await expect(
      page.locator(
        '.pl-inventory-scope-note'
      )
    ).toContainText(
      /Historical inventory snapshots are not available/i
    )
  }
)


test(
  'Inventory V2 is mobile-safe',
  async ({
    page,
  }) => {
    await page.setViewportSize({
      width: 390,
      height: 844,
    })

    await page.goto(
      '/inventory'
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

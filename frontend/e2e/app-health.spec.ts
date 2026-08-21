import {
  expect,
  test,
} from '@playwright/test'


const pages = [
  {
    name: 'Overview',
    path: '/',
  },
  {
    name: 'Products',
    path: '/products',
  },
  {
    name: 'Customers',
    path: '/customers',
  },
  {
    name: 'Logistics',
    path: '/logistics',
  },
  {
    name: 'Marketing',
    path: '/marketing',
  },
  {
    name: 'Inventory',
    path: '/inventory',
  },
  {
    name: 'Ask ProfitLens',
    path: '/analyst',
  },
  {
    name: 'Scenario Lab',
    path: '/scenario',
  },
]


for (
  const pageInfo of pages
) {
  test(
    `${pageInfo.name} loads without critical errors`,
    async ({
      page,
    }) => {
      const consoleErrors:
        string[] = []

      const failedRequests:
        string[] = []


      page.on(
        'console',
        message => {
          if (
            message.type()
            === 'error'
          ) {
            consoleErrors.push(
              message.text()
            )
          }
        }
      )


      page.on(
        'requestfailed',
        request => {
          failedRequests.push(
            `${request.method()} ${request.url()}`
          )
        }
      )


      await page.goto(
        pageInfo.path
      )


      await expect(
        page.locator(
          'body'
        )
      ).toBeVisible()


      await expect(
        page
      ).toHaveTitle(
        /ProfitLens/i
      )


      const bodyText =
        await page
          .locator(
            'body'
          )
          .innerText()


      const forbiddenValues = [
        'undefined',
        'NaN',
        '[object Object]',
        'np.float64',
        'Internal Server Error',
      ]


      for (
        const forbiddenValue
        of forbiddenValues
      ) {
        expect(
          bodyText
        ).not.toContain(
          forbiddenValue
        )
      }


      expect(
        consoleErrors,
        `Console errors on ${pageInfo.name}:\n${consoleErrors.join('\n')}`
      ).toEqual([])


      expect(
        failedRequests,
        `Failed requests on ${pageInfo.name}:\n${failedRequests.join('\n')}`
      ).toEqual([])


      await page.screenshot({
        path:
          `qa-screenshots/${pageInfo.name
            .toLowerCase()
            .replaceAll(' ', '-')}.png`,

        fullPage: true,
      })
    }
  )
}
const { chromium } = require('playwright')

;(async () => {
  const browser = await chromium.launch({
    headless: true,
  })

  const page = await browser.newPage({
    viewport: {
      width: 390,
      height: 844,
    },
  })

  const routes = [
    ['/products', 'Products'],
    ['/customers', 'Customers'],
    ['/logistics', 'Logistics'],
    ['/marketing', 'Marketing'],
    ['/inventory', 'Inventory'],
  ]

  for (const [path, name] of routes) {
    await page.goto(
      `http://127.0.0.1:5173${path}`
    )

    await page.waitForTimeout(1800)

    const result = await page.evaluate(() => {
      const viewport =
        document.documentElement.clientWidth

      const offenders = []

      document
        .querySelectorAll('*')
        .forEach((element) => {
          const rect =
            element.getBoundingClientRect()

          if (
            rect.right > viewport + 2
            || rect.width > viewport + 2
          ) {
            const style =
              window.getComputedStyle(
                element
              )

            offenders.push({
              tag:
                element.tagName,

              class:
                element.className
                  ?.toString()
                  .slice(0, 120),

              width:
                Math.round(
                  rect.width
                ),

              left:
                Math.round(
                  rect.left
                ),

              right:
                Math.round(
                  rect.right
                ),

              minWidth:
                style.minWidth,

              whiteSpace:
                style.whiteSpace,

              overflowX:
                style.overflowX,
            })
          }
        })

      return {
        viewport,

        documentWidth:
          document.documentElement
            .scrollWidth,

        offenders:
          offenders.slice(
            0,
            25
          ),
      }
    })

    console.log(
      '\n' + '='.repeat(80)
    )

    console.log(name)

    console.log(
      '='.repeat(80)
    )

    console.log(
      JSON.stringify(
        result,
        null,
        2
      )
    )
  }

  await browser.close()
})()

import {
  expect,
  test,
} from '@playwright/test'


test(
  'Ask ProfitLens V2 renders executive answer structure',
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
        'Why did revenue decline?'
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

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            /What supports the answer/i,
        }
      )
    ).toBeVisible()

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            /Likely driver/i,
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-analyst-meta'
      )
    ).toBeVisible()
  }
)


test(
  'Ask ProfitLens V2 exposes follow-up questions',
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

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            /Ask a follow-up/i,
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-analyst-followups button'
      ).first()
    ).toBeVisible()
  }
)


test(
  'Ask ProfitLens V2 follow-up can run another analysis',
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

    const followUp =
      page.locator(
        '.pl-analyst-followups button'
      ).first()

    const text =
      (
        await followUp
          .innerText()
      ).trim()

    await followUp.click()

    await expect(
      page.getByPlaceholder(
        'Ask a business question...'
      )
    ).toHaveValue(
      text
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
  'Ask ProfitLens V2 links analysis to relevant dashboard',
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
        'Which products generated the most revenue?'
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

    await page
      .getByRole(
        'button',
        {
          name:
            /Open Product Analysis/i,
        }
      )
      .click()

    await expect(
      page
    ).toHaveURL(
      /\/products/
    )
  }
)


test(
  'Ask ProfitLens V2 links to investigations',
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

    await page
      .getByRole(
        'button',
        {
          name:
            'View Investigations',
        }
      )
      .click()

    await expect(
      page
    ).toHaveURL(
      /\/investigations/
    )
  }
)


test(
  'Ask ProfitLens V2 links to Scenario Lab',
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
        'Why did revenue decline?'
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

    await page
      .getByRole(
        'button',
        {
          name:
            'Test Scenario',
        }
      )
      .click()

    await expect(
      page
    ).toHaveURL(
      /\/scenario/
    )
  }
)


test(
  'Ask ProfitLens V2 clears stale answer when month changes',
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
        'Why did revenue decline?'
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

    const monthSelect =
      page.locator(
        '.month-selector select'
      )

    await monthSelect
      .selectOption(
        '2025-10'
      )

    await expect(
      monthSelect
    ).toHaveValue(
      '2025-10'
    )

    await expect(
      page.locator(
        '.analyst-main-answer'
      )
    ).toHaveCount(
      0
    )
  }
)


test(
  'Ask ProfitLens V2 shows deterministic truth guardrail',
  async ({
    page,
  }) => {
    await page.goto(
      '/analyst'
    )

    await expect(
      page.locator(
        '.pl-analyst-guardrail'
      )
    ).toContainText(
      /deterministic analytics/i
    )

    await expect(
      page.locator(
        '.pl-analyst-guardrail'
      )
    ).toContainText(
      /AI may interpret/i
    )
  }
)


test(
  'Ask ProfitLens V2 is mobile-safe',
  async ({
    page,
  }) => {
    await page.setViewportSize({
      width: 390,
      height: 844,
    })

    await page.goto(
      '/analyst'
    )

    await page.waitForTimeout(
      1200
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


test(
  'Ask ProfitLens V2 shows four deterministic revenue steps',
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
        'Why did revenue decline?'
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

    const execution =
      page.locator(
        '.pl-analyst-execution-list'
      )

    await expect(
      execution
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-analyst-execution-row'
      )
    ).toHaveCount(
      4
    )

    await expect(
      execution
    ).toContainText(
      /Revenue Performance/i
    )

    await expect(
      execution
    ).toContainText(
      /Order Performance/i
    )

    await expect(
      execution
    ).toContainText(
      /Aov Performance/i
    )

    await expect(
      execution
    ).toContainText(
      /Profitability Context/i
    )

    await expect(
      page.locator(
        '.pl-analyst-execution-summary'
      )
    ).toContainText(
      /4\s*\/\s*4/i
    )

    await expect(
      page.locator(
        '.pl-analyst-execution-status.complete'
      )
    ).toHaveCount(
      4
    )
  }
)


test(
  'Ask ProfitLens V2 shows seven business health analysis steps',
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

    await expect(
      page.locator(
        '.pl-analyst-execution-row'
      )
    ).toHaveCount(
      7
    )

    await expect(
      page.locator(
        '.pl-analyst-execution-summary'
      )
    ).toContainText(
      /7\s*\/\s*7/i
    )

    const execution =
      page.locator(
        '.pl-analyst-execution-list'
      )

    await expect(
      execution
    ).toContainText(
      /Overview Performance/i
    )

    await expect(
      execution
    ).toContainText(
      /Profitability Context/i
    )

    await expect(
      execution
    ).toContainText(
      /Marketing Performance/i
    )

    await expect(
      execution
    ).toContainText(
      /Customer Performance/i
    )

    await expect(
      execution
    ).toContainText(
      /Logistics Performance/i
    )

    await expect(
      execution
    ).toContainText(
      /Inventory Performance/i
    )

    await expect(
      execution
    ).toContainText(
      /Product Performance/i
    )
  }
)


test(
  'Ask ProfitLens V2 shows revenue claim confidence',
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
        'Why did revenue decline?'
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

    await expect(
      page.locator(
        '.pl-claim-summary'
      )
    ).toContainText(
      /3 facts/i
    )

    await expect(
      page.locator(
        '.pl-claim-summary'
      )
    ).toContainText(
      /1 inference/i
    )

    await expect(
      page.locator(
        '.pl-claim-type.fact'
      )
    ).toHaveCount(
      3
    )

    await expect(
      page.locator(
        '.pl-claim-type.inference'
      )
    ).toHaveCount(
      1
    )

    await expect(
      page.locator(
        '.pl-claim-confidence.high'
      )
    ).toHaveCount(
      4
    )

    await expect(
      page.locator(
        '.pl-claim-list'
      )
    ).toContainText(
      /Lower order volume is the strongest observed commercial signal/i
    )

    await expect(
      page.locator(
        '.pl-claim-limitation'
      ).filter({
        hasText:
          /not a causal revenue decomposition/i,
      })
    ).toHaveCount(
      1
    )

    await expect(
      page.locator(
        '.pl-claim-definition'
      )
    ).toContainText(
      /not AI\/model confidence/i
    )
  }
)


test(
  'Ask ProfitLens V2 shows business health facts and inferences',
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

    await expect(
      page.locator(
        '.pl-claim-summary'
      )
    ).toContainText(
      /9 facts/i
    )

    await expect(
      page.locator(
        '.pl-claim-summary'
      )
    ).toContainText(
      /2 inferences/i
    )

    await expect(
      page.locator(
        '.pl-claim-type.fact'
      )
    ).toHaveCount(
      9
    )

    await expect(
      page.locator(
        '.pl-claim-type.inference'
      )
    ).toHaveCount(
      2
    )

    const claims =
      page.locator(
        '.pl-claim-list'
      )

    await expect(
      claims
    ).toContainText(
      /Realized revenue declined/i
    )

    await expect(
      claims
    ).toContainText(
      /COD is the strongest observed payment-related RTO risk signal/i
    )

    await expect(
      claims
    ).toContainText(
      /Estimated trapped inventory cost/i
    )

    await expect(
      page.locator(
        '.pl-claim-type.hypothesis'
      )
    ).toHaveCount(
      0
    )
  }
)


test(
  'Ask ProfitLens V2 shows unresolved revenue hypotheses and evidence gaps',
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
        'Why did revenue decline?'
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

    await expect(
      page.locator(
        '.pl-hypothesis-summary'
      )
    ).toContainText(
      /3 hypotheses/i
    )

    await expect(
      page.locator(
        '.pl-hypothesis-summary'
      )
    ).toContainText(
      /6 evidence gaps/i
    )

    await expect(
      page.locator(
        '.pl-hypothesis-card'
      )
    ).toHaveCount(
      3
    )

    await expect(
      page.locator(
        '.pl-hypothesis-status.insufficient_evidence'
      )
    ).toHaveCount(
      3
    )

    const section =
      page.locator(
        '.pl-hypothesis-list'
      )

    await expect(
      section
    ).toContainText(
      /Lower customer demand or lower qualified traffic/i
    )

    await expect(
      section
    ).toContainText(
      /Weaker customer acquisition/i
    )

    await expect(
      section
    ).toContainText(
      /Product availability constraints/i
    )

    await expect(
      page.locator(
        '.pl-hypothesis-guardrail'
      )
    ).toContainText(
      /possible explanations only/i
    )
  }
)


test(
  'Ask ProfitLens V2 shows unresolved logistics hypotheses',
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

    await expect(
      page.locator(
        '.pl-hypothesis-summary'
      )
    ).toContainText(
      /3 hypotheses/i
    )

    await expect(
      page.locator(
        '.pl-hypothesis-summary'
      )
    ).toContainText(
      /6 evidence gaps/i
    )

    await expect(
      page.locator(
        '.pl-hypothesis-card'
      )
    ).toHaveCount(
      3
    )

    const section =
      page.locator(
        '.pl-hypothesis-list'
      )

    await expect(
      section
    ).toContainText(
      /COD orders may contribute/i
    )

    await expect(
      section
    ).toContainText(
      /NDR-resolution inefficiency/i
    )

    await expect(
      section
    ).toContainText(
      /Courier or geographic mix/i
    )
  }
)


test(
  'Ask ProfitLens V2 shows business health evidence gaps without claiming root causes',
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

    await expect(
      page.locator(
        '.pl-hypothesis-summary'
      )
    ).toContainText(
      /4 hypotheses/i
    )

    await expect(
      page.locator(
        '.pl-hypothesis-summary'
      )
    ).toContainText(
      /8 evidence gaps/i
    )

    await expect(
      page.locator(
        '.pl-hypothesis-card'
      )
    ).toHaveCount(
      4
    )

    await expect(
      page.locator(
        '.pl-hypothesis-status.insufficient_evidence'
      )
    ).toHaveCount(
      4
    )

    await expect(
      page.getByRole(
        'heading',
        {
          name:
            'What we still need to prove',
        }
      )
    ).toBeVisible()

    await expect(
      page.locator(
        '.pl-hypothesis-guardrail'
      )
    ).toContainText(
      /must not be presented as established causes/i
    )

    const hypothesisText =
      await page
        .locator(
          '.pl-hypothesis-list'
        )
        .innerText()

    expect(
      hypothesisText
        .toLowerCase()
    ).not.toContain(
      'root cause'
    )
  }
)


test(
  'Ask ProfitLens V2 marks inventory actions as Act now',
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
        'Which inventory problems require immediate action?'
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

    await expect(
      page.locator(
        '.pl-recommendation-card'
      )
    ).toHaveCount(
      2
    )

    await expect(
      page.locator(
        '.pl-recommendation-readiness.act_now'
      )
    ).toHaveCount(
      2
    )

    await expect(
      page.locator(
        '.pl-recommendation-list'
      )
    ).toContainText(
      /highest trapped-inventory positions/i
    )

    await expect(
      page.locator(
        '.pl-recommendation-list'
      )
    ).toContainText(
      /below-reorder SKU-warehouse positions/i
    )
  }
)


test(
  'Ask ProfitLens V2 gates COD action as Test first',
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

    await expect(
      page.locator(
        '.pl-recommendation-readiness.test_first'
      )
    ).toHaveCount(
      1
    )

    const testFirstCard =
      page.locator(
        '.pl-recommendation-card'
      ).filter({
        has:
          page.locator(
            '.pl-recommendation-readiness.test_first'
          ),
      })

    await expect(
      testFirstCard
    ).toContainText(
      /Pilot stronger COD confirmation controls/i
    )

    await expect(
      testFirstCard
    ).toContainText(
      /measured pilot rather than a blanket COD restriction/i
    )
  }
)


test(
  'Ask ProfitLens V2 blocks unsupported ROAS-only action',
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

    await expect(
      page.locator(
        '.analyst-main-answer'
      )
    ).toBeVisible({
      timeout: 15000,
    })

    await expect(
      page.locator(
        '.pl-recommendation-readiness.do_not_act'
      )
    ).toHaveCount(
      1
    )

    await expect(
      page.locator(
        '.pl-recommendation-list'
      )
    ).toContainText(
      /Do not scale or cut marketing solely from aggregate ROAS/i
    )

    await expect(
      page.locator(
        '.pl-recommendation-list'
      )
    ).toContainText(
      /does not measure incrementality/i
    )
  }
)


test(
  'Ask ProfitLens V2 business health exposes all action readiness levels',
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

    await expect(
      page.locator(
        '.pl-recommendation-card'
      )
    ).toHaveCount(
      6
    )

    await expect(
      page.locator(
        '.pl-recommendation-readiness.act_now'
      )
    ).toHaveCount(
      3
    )

    await expect(
      page.locator(
        '.pl-recommendation-readiness.test_first'
      )
    ).toHaveCount(
      1
    )

    await expect(
      page.locator(
        '.pl-recommendation-readiness.investigate_first'
      )
    ).toHaveCount(
      1
    )

    await expect(
      page.locator(
        '.pl-recommendation-readiness.do_not_act'
      )
    ).toHaveCount(
      1
    )

    await expect(
      page.locator(
        '.pl-recommendation-definition'
      )
    ).toContainText(
      /not AI confidence/i
    )
  }
)


test(
  'Ask ProfitLens V2 uses recommendation gate as the D2C action authority',
  async ({
    page,
  }) => {
    await page.goto(
      '/analyst'
    )

    const responsePromise =
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

    const response =
      await responsePromise

    const body =
      await response.json()

    const gated =
      body
        .recommendation_analysis
        .recommendations

    const positiveGatedActions =
      gated
        .filter(
          (
            item: {
              readiness: string
            }
          ) =>
            item.readiness
            !== 'do_not_act'
        )
        .map(
          (
            item: {
              action: string
            }
          ) =>
            item.action
        )

    expect(
      body
        .answer
        .recommended_actions
    ).toEqual(
      positiveGatedActions
    )

    expect(
      body
        .answer
        .recommended_actions
    ).not.toContain(
      'Do not broadly disable COD based only on the observed RTO gap.'
    )

    await expect(
      page.locator(
        '.pl-recommendation-readiness.test_first'
      )
    ).toHaveCount(
      1
    )

    await expect(
      page.locator(
        '.pl-recommendation-readiness.do_not_act'
      )
    ).toHaveCount(
      1
    )
  }
)

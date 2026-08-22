import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowRight,
  Boxes,
  Package,
  RefreshCcw,
  RotateCcw,
  Search,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from 'lucide-react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  api,
} from '../api/profitlens'

import {
  MetricCard,
} from '../components/metrics/MetricCard'

import {
  MetricDrilldownDrawer,
} from '../components/metrics/MetricDrilldownDrawer'

import {
  useMetricDrilldown,
} from '../components/metrics/useMetricDrilldown'

import type {
  D2CCategoryRow,
  D2CProductRow,
  D2CProductsResponse,
} from '../types/api'

import type {
  MetricContract,
  MetricUnit,
} from '../types/metric'


type ProductsProps = {
  month: string
}


type RiskFilter =
  | 'all'
  | 'loss'
  | 'high-rto'
  | 'high-returns'


function formatCurrency(
  value: number
) {
  return new Intl.NumberFormat(
    'en-IN',
    {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }
  ).format(
    value
  )
}


function formatCompactCurrency(
  value: number
) {
  return new Intl.NumberFormat(
    'en-IN',
    {
      style: 'currency',
      currency: 'INR',
      notation: 'compact',
      maximumFractionDigits: 1,
    }
  ).format(
    value
  )
}


function formatNumber(
  value: number
) {
  return new Intl.NumberFormat(
    'en-IN'
  ).format(
    value
  )
}


function metric(
  input: {
    metricId: string
    label: string
    value: number
    formattedValue: string
    unit: MetricUnit
    higherIsBetter: boolean
    definition?: string
  }
): MetricContract {
  return {
    metric_id:
      input.metricId,

    label:
      input.label,

    value:
      input.value,

    formatted_value:
      input.formattedValue,

    unit:
      input.unit,

    comparison: {
      previous_value:
        null,

      change_absolute:
        null,

      change_percent:
        null,

      direction:
        'unknown',
    },

    sentiment:
      'neutral',

    definition:
      input.definition
      ?? null,

    formula:
      null,

    data_quality:
      'verified',

    source: {
      engine:
        null,

      tables:
        [],

      fields:
        [],
    },

    metadata: {
      higher_is_better:
        input.higherIsBetter,
    },
  }
}


export default function Products({
  month,
}: ProductsProps) {
  const navigate =
    useNavigate()

  const drilldown =
    useMetricDrilldown()

  const [
    productData,
    setProductData,
  ] = useState<
    D2CProductsResponse | null
  >(
    null
  )

  const [
    categories,
    setCategories,
  ] = useState<
    D2CCategoryRow[]
  >(
    []
  )

  const [
    loading,
    setLoading,
  ] = useState(
    true
  )

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(
    null
  )

  const [
    search,
    setSearch,
  ] = useState('')

  const [
    categoryFilter,
    setCategoryFilter,
  ] = useState(
    'All'
  )

  const [
    riskFilter,
    setRiskFilter,
  ] = useState<RiskFilter>(
    'all'
  )


  useEffect(
    () => {
      let cancelled =
        false

      setLoading(true)
      setError(null)

      Promise.all([
        api.products(
          month
        ),

        api.categories(
          month
        ),
      ])
        .then(
          ([
            productsResponse,
            categoriesResponse,
          ]) => {
            if (
              cancelled
            ) {
              return
            }

            setProductData(
              productsResponse
            )

            setCategories(
              categoriesResponse.categories
            )
          }
        )
        .catch(
          requestError => {
            if (
              cancelled
            ) {
              return
            }

            setProductData(
              null
            )

            setCategories(
              []
            )

            setError(
              requestError
                instanceof Error
                ? requestError.message
                : (
                    'Could not load '
                    + 'product analytics.'
                  )
            )
          }
        )
        .finally(
          () => {
            if (
              !cancelled
            ) {
              setLoading(
                false
              )
            }
          }
        )


      return () => {
        cancelled = true
      }
    },
    [
      month,
    ]
  )


  const summary =
    productData
      ?.summary
    ?? null


  const metrics =
    useMemo(
      () => {
        if (
          !summary
        ) {
          return []
        }

        return [
          metric({
            metricId:
              'product_net_revenue',

            label:
              'Net Revenue',

            value:
              summary
                .total_net_revenue,

            formattedValue:
              formatCurrency(
                summary
                  .total_net_revenue
              ),

            unit:
              'currency',

            higherIsBetter:
              true,
          }),

          metric({
            metricId:
              'product_gross_profit',

            label:
              'Gross Profit',

            value:
              summary
                .total_gross_profit,

            formattedValue:
              formatCurrency(
                summary
                  .total_gross_profit
              ),

            unit:
              'currency',

            higherIsBetter:
              true,
          }),

          metric({
            metricId:
              'product_gross_margin',

            label:
              'Gross Margin',

            value:
              summary
                .gross_margin_percent,

            formattedValue:
              `${summary
                .gross_margin_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              true,
          }),

          metric({
            metricId:
              'loss_making_products',

            label:
              'Loss-Making SKUs',

            value:
              summary
                .loss_making_products,

            formattedValue:
              formatNumber(
                summary
                  .loss_making_products
              ),

            unit:
              'count',

            higherIsBetter:
              false,
          }),

          metric({
            metricId:
              'top_5_revenue_share',

            label:
              'Top 5 Revenue Share',

            value:
              summary
                .top_5_revenue_share_percent,

            formattedValue:
              `${summary
                .top_5_revenue_share_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              false,
          }),

          metric({
            metricId:
              'top_10_revenue_share',

            label:
              'Top 10 Revenue Share',

            value:
              summary
                .top_10_revenue_share_percent,

            formattedValue:
              `${summary
                .top_10_revenue_share_percent
                .toFixed(2)}%`,

            unit:
              'percent',

            higherIsBetter:
              false,
          }),
        ]
      },
      [
        summary,
      ]
    )


  const revenueLeaders =
    useMemo(
      () =>
        (
          productData
            ?.products
          ?? []
        )
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second.net_revenue
              - first.net_revenue
          )
          .slice(
            0,
            6
          ),
      [
        productData,
      ]
    )


  const marginLeaders =
    useMemo(
      () =>
        (
          productData
            ?.products
          ?? []
        )
          .filter(
            row =>
              row.net_revenue
              > 0
          )
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second
                .gross_margin_percent
              - first
                .gross_margin_percent
          )
          .slice(
            0,
            6
          ),
      [
        productData,
      ]
    )


  const riskProducts =
    useMemo(
      () =>
        (
          productData
            ?.products
          ?? []
        )
          .slice()
          .sort(
            (
              first,
              second,
            ) => {
              const firstRisk =
                first.rto_rate_percent
                + first.return_rate_percent

              const secondRisk =
                second.rto_rate_percent
                + second.return_rate_percent

              return (
                secondRisk
                - firstRisk
              )
            }
          )
          .slice(
            0,
            6
          ),
      [
        productData,
      ]
    )


  const categoryLeaders =
    useMemo(
      () =>
        categories
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second.net_revenue
              - first.net_revenue
          ),
      [
        categories,
      ]
    )


  const filteredProducts =
    useMemo(
      () => {
        if (
          !productData
        ) {
          return []
        }

        const normalizedSearch =
          search
            .trim()
            .toLowerCase()

        return productData
          .products
          .filter(
            row => {
              const matchesSearch =
                !normalizedSearch
                || row.sku_id
                  .toLowerCase()
                  .includes(
                    normalizedSearch
                  )
                || row.product_name
                  .toLowerCase()
                  .includes(
                    normalizedSearch
                  )

              const matchesCategory =
                categoryFilter
                === 'All'
                || row.category
                === categoryFilter

              let matchesRisk =
                true

              if (
                riskFilter
                === 'loss'
              ) {
                matchesRisk =
                  row.gross_profit
                  < 0
              }

              if (
                riskFilter
                === 'high-rto'
              ) {
                matchesRisk =
                  row.rto_rate_percent
                  >= 15
              }

              if (
                riskFilter
                === 'high-returns'
              ) {
                matchesRisk =
                  row.return_rate_percent
                  >= 10
              }

              return (
                matchesSearch
                && matchesCategory
                && matchesRisk
              )
            }
          )
      },
      [
        productData,
        search,
        categoryFilter,
        riskFilter,
      ]
    )


  function openMetric(
    selected:
      MetricContract
  ) {
    if (
      selected.value
      === null
      || selected.value
      === undefined
    ) {
      return
    }

    void drilldown.openMetric({
      metricId:
        selected.metric_id,

      value:
        Number(
          selected.value
        ),
    })
  }


  if (
    loading
  ) {
    return (
      <div className="pl-products-v2">

        <div className="pl-page-state">

          <RefreshCcw
            size={20}
          />

          Loading product analytics...

        </div>

      </div>
    )
  }


  if (
    error
    || !productData
    || !summary
  ) {
    return (
      <div className="pl-products-v2">

        <div className="pl-page-state error">

          <AlertTriangle
            size={20}
          />

          <div>

            <strong>
              Could not load products
            </strong>

            <span>
              {
                error
                ?? 'Product data is unavailable.'
              }
            </span>

          </div>

        </div>

      </div>
    )
  }


  return (
    <div className="pl-products-v2">

      <section className="pl-business-hero">

        <div>

          <div className="pl-page-eyebrow">
            Portfolio intelligence
          </div>

          <h1>
            Product Performance
          </h1>

          <p>
            Identify products driving revenue,
            gross profit and operational risk
            for {month}.
          </p>

        </div>


        <div className="pl-business-hero-actions">

          <button
            type="button"
            className="pl-secondary-button"
            onClick={() =>
              navigate(
                '/analyst'
              )
            }
          >

            <Sparkles
              size={14}
            />

            Ask ProfitLens

          </button>


          <button
            type="button"
            className="pl-primary-button"
            onClick={() =>
              navigate(
                '/investigations'
              )
            }
          >

            Investigate products

            <ArrowRight
              size={14}
            />

          </button>

        </div>

      </section>


      <section className="pl-product-strip">

        <div>

          <Package
            size={17}
          />

          <span>
            Products
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .total_products
              )
            }
          </strong>

        </div>


        <div>

          <TrendingUp
            size={17}
          />

          <span>
            Portfolio Revenue
          </span>

          <strong>
            {
              formatCompactCurrency(
                summary
                  .total_net_revenue
              )
            }
          </strong>

        </div>


        <div>

          <Boxes
            size={17}
          />

          <span>
            Top 5 Share
          </span>

          <strong>
            {
              summary
                .top_5_revenue_share_percent
                .toFixed(2)
            }%
          </strong>

        </div>


        <div>

          <AlertTriangle
            size={17}
          />

          <span>
            Loss Makers
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .loss_making_products
              )
            }
          </strong>

        </div>

      </section>


      <section>

        <div className="pl-section-header">

          <div>

            <h2>
              Product health
            </h2>

            <p>
              Portfolio economics,
              concentration and profitability.
            </p>

          </div>

        </div>


        <div className="pl-metric-grid">

          {
            metrics.map(
              item => (
                <MetricCard
                  key={
                    item.metric_id
                  }
                  metric={
                    item
                  }
                  onClick={
                    openMetric
                  }
                />
              )
            )
          }

        </div>

      </section>


      <section className="pl-product-analysis-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Revenue winners
              </span>

              <h2>
                Highest revenue products
              </h2>

            </div>

          </div>


          <div className="pl-product-ranking-list">

            {
              revenueLeaders.map(
                row => (
                  <div
                    key={
                      row.sku_id
                    }
                    className="pl-product-ranking-row"
                  >

                    <div>

                      <strong>
                        {
                          row.product_name
                        }
                      </strong>

                      <span>
                        {
                          row.sku_id
                        }
                        {' · '}
                        {
                          row.category
                        }
                      </span>

                    </div>


                    <div>

                      <span>
                        Revenue
                      </span>

                      <strong>
                        {
                          formatCurrency(
                            row.net_revenue
                          )
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Margin
                      </span>

                      <strong>
                        {
                          row
                            .gross_margin_percent
                            .toFixed(2)
                        }%
                      </strong>

                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>


        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Margin leaders
              </span>

              <h2>
                Highest gross-margin products
              </h2>

            </div>

          </div>


          <div className="pl-product-ranking-list">

            {
              marginLeaders.map(
                row => (
                  <div
                    key={
                      row.sku_id
                    }
                    className="pl-product-ranking-row"
                  >

                    <div>

                      <strong>
                        {
                          row.product_name
                        }
                      </strong>

                      <span>
                        {
                          row.sku_id
                        }
                        {' · '}
                        {
                          row.category
                        }
                      </span>

                    </div>


                    <div>

                      <span>
                        Margin
                      </span>

                      <strong>
                        {
                          row
                            .gross_margin_percent
                            .toFixed(2)
                        }%
                      </strong>

                    </div>


                    <div>

                      <span>
                        Gross Profit
                      </span>

                      <strong>
                        {
                          formatCurrency(
                            row.gross_profit
                          )
                        }
                      </strong>

                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>

      </section>


      <section className="pl-product-analysis-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Operational risk
              </span>

              <h2>
                Products needing attention
              </h2>

            </div>

          </div>


          <div className="pl-product-ranking-list">

            {
              riskProducts.map(
                row => (
                  <div
                    key={
                      row.sku_id
                    }
                    className="pl-product-ranking-row risk"
                  >

                    <div>

                      <strong>
                        {
                          row.product_name
                        }
                      </strong>

                      <span>
                        {
                          row.sku_id
                        }
                        {' · '}
                        {
                          row.category
                        }
                      </span>

                    </div>


                    <div>

                      <span>
                        RTO
                      </span>

                      <strong>
                        {
                          row
                            .rto_rate_percent
                            .toFixed(2)
                        }%
                      </strong>

                    </div>


                    <div>

                      <span>
                        Returns
                      </span>

                      <strong>
                        {
                          row
                            .return_rate_percent
                            .toFixed(2)
                        }%
                      </strong>

                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>


        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Category economics
              </span>

              <h2>
                Revenue and margin by category
              </h2>

            </div>

          </div>


          <div className="pl-product-category-list">

            {
              categoryLeaders.map(
                row => (
                  <div
                    key={
                      row.category
                    }
                    className="pl-product-category-row"
                  >

                    <strong>
                      {
                        row.category
                      }
                    </strong>


                    <div>

                      <span>
                        Revenue
                      </span>

                      <strong>
                        {
                          formatCompactCurrency(
                            row.net_revenue
                          )
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Margin
                      </span>

                      <strong>
                        {
                          row
                            .gross_margin_percent
                            .toFixed(2)
                        }%
                      </strong>

                    </div>


                    <div>

                      <span>
                        RTO
                      </span>

                      <strong>
                        {
                          row
                            .rto_rate_percent
                            .toFixed(2)
                        }%
                      </strong>

                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>

      </section>


      <section className="pl-founder-panel">

        <div className="pl-panel-header">

          <div>

            <span className="pl-page-eyebrow">
              Category comparison
            </span>

            <h2>
              Category performance
            </h2>

          </div>

        </div>


        <div className="table-wrap">

          <table className="data-table">

            <thead>

              <tr>
                <th>Category</th>
                <th>Products</th>
                <th>Orders</th>
                <th>Revenue</th>
                <th>Gross Profit</th>
                <th>Margin</th>
                <th>Revenue Share</th>
                <th>RTO</th>
                <th>Returns</th>
              </tr>

            </thead>


            <tbody>

              {
                categories.map(
                  row => (
                    <tr
                      key={
                        row.category
                      }
                    >

                      <td>
                        <strong>
                          {
                            row.category
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          formatNumber(
                            row.products
                          )
                        }
                      </td>

                      <td>
                        {
                          formatNumber(
                            row.orders
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row.net_revenue
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row.gross_profit
                          )
                        }
                      </td>

                      <td>
                        {
                          row
                            .gross_margin_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          row
                            .revenue_share_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          row
                            .rto_rate_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          row
                            .return_rate_percent
                            .toFixed(2)
                        }%
                      </td>

                    </tr>
                  )
                )
              }

            </tbody>

          </table>

        </div>

      </section>


      <section className="pl-founder-panel">

        <div className="pl-panel-header">

          <div>

            <span className="pl-page-eyebrow">
              SKU control centre
            </span>

            <h2>
              Product explorer
            </h2>

          </div>


          <strong className="pl-product-result-count">
            {
              formatNumber(
                filteredProducts.length
              )
            } SKUs
          </strong>

        </div>


        <div className="pl-product-filters">

          <label className="pl-product-search">

            <Search
              size={15}
            />

            <input
              value={
                search
              }
              onChange={
                event =>
                  setSearch(
                    event.target.value
                  )
              }
              placeholder="Search SKU or product..."
            />

          </label>


          <select
            value={
              categoryFilter
            }
            onChange={
              event =>
                setCategoryFilter(
                  event.target.value
                )
            }
            aria-label="Product category"
          >

            <option value="All">
              All categories
            </option>

            {
              categories.map(
                row => (
                  <option
                    key={
                      row.category
                    }
                    value={
                      row.category
                    }
                  >
                    {
                      row.category
                    }
                  </option>
                )
              )
            }

          </select>


          <select
            value={
              riskFilter
            }
            onChange={
              event =>
                setRiskFilter(
                  event.target.value as RiskFilter
                )
            }
            aria-label="Product risk"
          >

            <option value="all">
              All products
            </option>

            <option value="loss">
              Loss-making
            </option>

            <option value="high-rto">
              High RTO
            </option>

            <option value="high-returns">
              High returns
            </option>

          </select>

        </div>


        <div className="table-wrap">

          <table className="data-table">

            <thead>

              <tr>
                <th>Product</th>
                <th>Category</th>
                <th>Orders</th>
                <th>Units</th>
                <th>Net Revenue</th>
                <th>Gross Profit</th>
                <th>Margin</th>
                <th>ASP</th>
                <th>RTO</th>
                <th>Returns</th>
              </tr>

            </thead>


            <tbody>

              {
                filteredProducts.map(
                  (
                    row:
                      D2CProductRow
                  ) => (
                    <tr
                      key={
                        row.sku_id
                      }
                    >

                      <td>

                        <strong>
                          {
                            row.product_name
                          }
                        </strong>

                        <div className="table-subtext">
                          {
                            row.sku_id
                          }
                        </div>

                      </td>

                      <td>
                        {
                          row.category
                        }
                      </td>

                      <td>
                        {
                          formatNumber(
                            row.orders
                          )
                        }
                      </td>

                      <td>
                        {
                          formatNumber(
                            row.units_sold
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row.net_revenue
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row.gross_profit
                          )
                        }
                      </td>

                      <td>

                        <span
                          className={
                            row.gross_margin_percent
                            >= 0
                              ? 'positive'
                              : 'negative'
                          }
                        >
                          {
                            row
                              .gross_margin_percent
                              .toFixed(2)
                          }%

                          {
                            row.gross_margin_percent
                            >= 0
                              ? (
                                  <TrendingUp
                                    size={12}
                                  />
                                )
                              : (
                                  <TrendingDown
                                    size={12}
                                  />
                                )
                          }

                        </span>

                      </td>

                      <td>
                        {
                          formatCurrency(
                            row
                              .average_selling_price
                          )
                        }
                      </td>

                      <td>

                        <span>
                          <RotateCcw
                            size={12}
                          />
                          {' '}
                          {
                            row
                              .rto_rate_percent
                              .toFixed(2)
                          }%
                        </span>

                      </td>

                      <td>
                        {
                          row
                            .return_rate_percent
                            .toFixed(2)
                        }%
                      </td>

                    </tr>
                  )
                )
              }

            </tbody>

          </table>

        </div>

      </section>


      <section className="pl-product-scope-note">

        <AlertTriangle
          size={20}
        />

        <div>

          <strong>
            Product profitability scope
          </strong>

          <p>
            SKU profitability currently ends
            at gross profit. Contribution profit
            is not allocated to individual SKUs
            because logistics, payment and
            marketing costs require a defined
            allocation methodology before
            deterministic SKU contribution
            profit can be calculated.
          </p>

        </div>

      </section>


      <MetricDrilldownDrawer
        open={
          drilldown.open
        }

        loading={
          drilldown.loading
        }

        error={
          drilldown.error
        }

        data={
          drilldown.data
        }

        onClose={
          drilldown.closeMetric
        }

        onSuggestedQuestion={() =>
          navigate(
            '/analyst'
          )
        }
      />

    </div>
  )
}

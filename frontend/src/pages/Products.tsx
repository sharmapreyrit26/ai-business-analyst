import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Boxes,
  Package,
  RotateCcw,
  Search,
  TrendingUp,
} from 'lucide-react'

import {
  api,
} from '../api/profitlens'

import type {
  D2CCategoryRow,
  D2CProductRow,
  D2CProductsResponse,
} from '../types/api'


type ProductsProps = {
  month: string
}


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
  ).format(value)
}


function formatNumber(
  value: number
) {
  return new Intl.NumberFormat(
    'en-IN'
  ).format(value)
}


export default function Products({
  month,
}: ProductsProps) {
  const [
    productData,
    setProductData,
  ] = useState<D2CProductsResponse | null>(
    null
  )

  const [
    categories,
    setCategories,
  ] = useState<D2CCategoryRow[]>(
    []
  )

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  )

  const [
    search,
    setSearch,
  ] = useState('')

  const [
    categoryFilter,
    setCategoryFilter,
  ] = useState('All')


  useEffect(
    () => {
      let cancelled = false

      setLoading(true)
      setError(null)

      Promise.all([
        api.products(month),
        api.categories(month),
      ])
        .then(
          ([
            productsResponse,
            categoriesResponse,
          ]) => {
            if (cancelled) {
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
          (
            requestError
          ) => {
            if (cancelled) {
              return
            }

            setProductData(null)
            setCategories([])

            setError(
              requestError
                instanceof Error
                ? requestError.message
                : 'Could not load product analytics.'
            )
          }
        )
        .finally(
          () => {
            if (!cancelled) {
              setLoading(false)
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


  const filteredProducts =
    useMemo(
      () => {
        if (!productData) {
          return []
        }

        const normalizedSearch =
          search
            .trim()
            .toLowerCase()

        return (
          productData.products.filter(
            (
              product
            ) => {
              const matchesSearch =
                !normalizedSearch
                || product.sku_id
                  .toLowerCase()
                  .includes(
                    normalizedSearch
                  )
                || product.product_name
                  .toLowerCase()
                  .includes(
                    normalizedSearch
                  )

              const matchesCategory =
                categoryFilter
                === 'All'
                || product.category
                === categoryFilter

              return (
                matchesSearch
                && matchesCategory
              )
            }
          )
        )
      },
      [
        productData,
        search,
        categoryFilter,
      ]
    )


  if (loading) {
    return (
      <div className="page">
        <div className="card">
          Loading product analytics...
        </div>
      </div>
    )
  }


  if (
    error
    || !productData
  ) {
    return (
      <div className="page">
        <div className="card error-card">
          <AlertTriangle
            size={20}
          />

          <div>
            <strong>
              Could not load products
            </strong>

            <p>
              {
                error
                || 'Unknown error'
              }
            </p>
          </div>
        </div>
      </div>
    )
  }


  const {
    summary,
  } = productData


  return (
    <div className="page">

      <div className="page-header">
        <div>
          <div className="eyebrow">
            Product analytics
          </div>

          <h2>
            Product Performance
          </h2>

          <p>
            Revenue, margin, RTO and return
            performance for {month}.
          </p>
        </div>
      </div>


      <div className="metric-grid">

        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Products
              </div>

              <div className="metric-value">
                {
                  formatNumber(
                    summary.total_products
                  )
                }
              </div>
            </div>

            <div className="metric-icon">
              <Package size={20} />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Net Revenue
              </div>

              <div className="metric-value">
                {
                  formatCurrency(
                    summary.total_net_revenue
                  )
                }
              </div>
            </div>

            <div className="metric-icon">
              <TrendingUp size={20} />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Gross Profit
              </div>

              <div className="metric-value">
                {
                  formatCurrency(
                    summary.total_gross_profit
                  )
                }
              </div>
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Gross Margin
              </div>

              <div className="metric-value">
                {
                  summary
                    .gross_margin_percent
                    .toFixed(2)
                }%
              </div>
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Loss-Making SKUs
              </div>

              <div className="metric-value">
                {
                  formatNumber(
                    summary.loss_making_products
                  )
                }
              </div>
            </div>

            <div className="metric-icon">
              <AlertTriangle
                size={20}
              />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Top 10 Revenue Share
              </div>

              <div className="metric-value">
                {
                  summary
                    .top_10_revenue_share_percent
                    .toFixed(2)
                }%
              </div>
            </div>

            <div className="metric-icon">
              <Boxes size={20} />
            </div>
          </div>
        </div>

      </div>


      <div className="section-heading">
        <div>
          <h2>
            Category Performance
          </h2>

          <p>
            Revenue, margin and logistics
            risk by category.
          </p>
        </div>
      </div>


      <div className="card">
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
                <th>RTO</th>
                <th>Returns</th>
              </tr>
            </thead>

            <tbody>
              {
                categories.map(
                  (
                    category
                  ) => (
                    <tr
                      key={
                        category.category
                      }
                    >
                      <td>
                        <strong>
                          {
                            category.category
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          formatNumber(
                            category.products
                          )
                        }
                      </td>

                      <td>
                        {
                          formatNumber(
                            category.orders
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            category.net_revenue
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            category.gross_profit
                          )
                        }
                      </td>

                      <td>
                        {
                          category
                            .gross_margin_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          category
                            .rto_rate_percent
                            .toFixed(2)
                        }%
                      </td>

                      <td>
                        {
                          category
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
      </div>


      <div className="section-heading">
        <div>
          <h2>
            SKU Performance
          </h2>

          <p>
            Search and inspect individual
            product economics.
          </p>
        </div>
      </div>


      <div className="card">

        <div className="filter-bar">

          <div className="search-control">
            <Search size={16} />

            <input
              value={search}
              onChange={
                (
                  event
                ) => setSearch(
                  event.target.value
                )
              }
              placeholder="Search SKU or product..."
            />
          </div>


          <select
            className="select"
            value={categoryFilter}
            onChange={
              (
                event
              ) => setCategoryFilter(
                event.target.value
              )
            }
          >
            <option value="All">
              All categories
            </option>

            {
              categories.map(
                (
                  category
                ) => (
                  <option
                    key={
                      category.category
                    }
                    value={
                      category.category
                    }
                  >
                    {
                      category.category
                    }
                  </option>
                )
              )
            }
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
                <th>Revenue</th>
                <th>Gross Profit</th>
                <th>Margin</th>
                <th>RTO</th>
                <th>Returns</th>
              </tr>
            </thead>

            <tbody>
              {
                filteredProducts.map(
                  (
                    product: D2CProductRow
                  ) => (
                    <tr
                      key={
                        product.sku_id
                      }
                    >

                      <td>
                        <div>
                          <strong>
                            {
                              product
                                .product_name
                            }
                          </strong>

                          <div className="table-subtext">
                            {
                              product.sku_id
                            }
                          </div>
                        </div>
                      </td>


                      <td>
                        {
                          product.category
                        }
                      </td>


                      <td>
                        {
                          formatNumber(
                            product.orders
                          )
                        }
                      </td>


                      <td>
                        {
                          formatNumber(
                            product.units_sold
                          )
                        }
                      </td>


                      <td>
                        {
                          formatCurrency(
                            product.net_revenue
                          )
                        }
                      </td>


                      <td>
                        {
                          formatCurrency(
                            product.gross_profit
                          )
                        }
                      </td>


                      <td>
                        <span
                          className={
                            product
                              .gross_margin_percent
                            < 0
                              ? 'negative'
                              : 'positive'
                          }
                        >
                          {
                            product
                              .gross_margin_percent
                              .toFixed(2)
                          }%

                          {
                            product
                              .gross_margin_percent
                            < 0
                              ? (
                                  <ArrowDownRight
                                    size={13}
                                  />
                                )
                              : (
                                  <ArrowUpRight
                                    size={13}
                                  />
                                )
                          }
                        </span>
                      </td>


                      <td>
                        <span>
                          <RotateCcw
                            size={13}
                          />{' '}
                          {
                            product
                              .rto_rate_percent
                              .toFixed(2)
                          }%
                        </span>
                      </td>


                      <td>
                        {
                          product
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


        <div className="table-footer">
          Showing {
            formatNumber(
              filteredProducts.length
            )
          } of {
            formatNumber(
              productData.products.length
            )
          } products
        </div>

      </div>


      <div className="card limitation-card">
        <strong>
          Profitability scope
        </strong>

        <p>
          Product profitability currently
          represents gross profit. SKU-level
          contribution profit is not yet shown
          because order-level logistics, payment
          and marketing costs require a defined
          allocation methodology.
        </p>
      </div>

    </div>
  )
}
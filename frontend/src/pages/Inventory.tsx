import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  Boxes,
  PackageSearch,
  Warehouse,
} from 'lucide-react'

import {
  api,
} from '../api/profitlens'

import type {
  D2CInventoryCategoryRow,
  D2CInventorySkuRow,
  D2CInventorySummaryResponse,
  D2CInventoryWarehouseRow,
} from '../types/api'


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


export default function Inventory() {
  const [
    summary,
    setSummary,
  ] = useState<D2CInventorySummaryResponse | null>(
    null
  )

  const [
    skus,
    setSkus,
  ] = useState<D2CInventorySkuRow[]>(
    []
  )

  const [
    warehouses,
    setWarehouses,
  ] = useState<D2CInventoryWarehouseRow[]>(
    []
  )

  const [
    categories,
    setCategories,
  ] = useState<D2CInventoryCategoryRow[]>(
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

  const [
    reorderOnly,
    setReorderOnly,
  ] = useState(false)


  useEffect(
    () => {
      let cancelled = false

      setLoading(true)
      setError(null)

      Promise.all([
        api.inventorySummary(),
        api.inventorySkus(),
        api.inventoryWarehouses(),
        api.inventoryCategories(),
      ])
        .then(
          ([
            summaryResponse,
            skuResponse,
            warehouseResponse,
            categoryResponse,
          ]) => {
            if (cancelled) {
              return
            }

            setSummary(
              summaryResponse
            )

            setSkus(
              skuResponse.data
            )

            setWarehouses(
              warehouseResponse.data
            )

            setCategories(
              categoryResponse.data
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

            setSummary(null)
            setSkus([])
            setWarehouses([])
            setCategories([])

            setError(
              requestError
                instanceof Error
                ? requestError.message
                : 'Could not load inventory analytics.'
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
    []
  )


  const filteredSkus =
    useMemo(
      () => {
        const normalizedSearch =
          search
            .trim()
            .toLowerCase()

        return skus.filter(
          (
            row
          ) => {
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

            const matchesReorder =
              !reorderOnly
              || row.is_reorder_candidate

            return (
              matchesSearch
              && matchesCategory
              && matchesReorder
            )
          }
        )
      },
      [
        skus,
        search,
        categoryFilter,
        reorderOnly,
      ]
    )


  if (loading) {
    return (
      <div className="page">
        <div className="card">
          Loading inventory analytics...
        </div>
      </div>
    )
  }


  if (
    error
    || !summary
  ) {
    return (
      <div className="page">
        <div className="card error-card">
          <AlertTriangle
            size={20}
          />

          <div>
            <strong>
              Could not load inventory
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


  return (
    <div className="page">

      <div className="page-header">
        <div>
          <div className="eyebrow">
            Inventory analytics
          </div>

          <h2>
            Inventory Health
          </h2>

          <p>
            Current stock position,
            reorder risk and estimated
            working-capital exposure.
          </p>
        </div>
      </div>


      <div className="metric-grid">

        <div className="card metric-card">
          <div className="metric-card-top">
            <div>
              <div className="metric-label">
                Inventory at Cost
              </div>

              <div className="metric-value">
                {
                  formatCurrency(
                    summary.inventory_cost_value
                  )
                }
              </div>
            </div>

            <div className="metric-icon">
              <Boxes size={20} />
            </div>
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Retail Value
          </div>

          <div className="metric-value">
            {
              formatCurrency(
                summary.inventory_retail_value
              )
            }
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Closing Stock
          </div>

          <div className="metric-value">
            {
              formatNumber(
                summary.total_closing_stock_units
              )
            }
          </div>

          <div className="metric-subtitle">
            units
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            SKUs
          </div>

          <div className="metric-value">
            {
              formatNumber(
                summary.total_skus
              )
            }
          </div>

          <div className="metric-subtitle">
            across {
              summary.warehouses
            } warehouses
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Below Reorder
          </div>

          <div className="metric-value">
            {
              formatNumber(
                summary.below_reorder_rows
              )
            }
          </div>

          <div className="metric-subtitle">
            SKU × warehouse positions
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Out of Stock
          </div>

          <div className="metric-value">
            {
              formatNumber(
                summary.out_of_stock_rows
              )
            }
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Revenue at Risk
          </div>

          <div className="metric-value">
            {
              formatCurrency(
                summary.potential_revenue_at_risk
              )
            }
          </div>

          <div className="metric-subtitle">
            reorder-gap estimate
          </div>
        </div>


        <div className="card metric-card">
          <div className="metric-label">
            Trapped Inventory
          </div>

          <div className="metric-value">
            {
              formatCurrency(
                summary
                  .estimated_trapped_inventory_cost
              )
            }
          </div>

          <div className="metric-subtitle">
            estimated excess stock at cost
          </div>
        </div>

      </div>


      <div className="section-heading">
        <div>
          <h2>
            Warehouse Health
          </h2>

          <p>
            Inventory position by fulfilment location.
          </p>
        </div>
      </div>


      <div className="card">
        <div className="table-wrap">
          <table className="data-table">

            <thead>
              <tr>
                <th>Warehouse</th>
                <th>SKUs</th>
                <th>Closing Stock</th>
                <th>Units Sold</th>
                <th>Inventory Cost</th>
                <th>Below Reorder</th>
                <th>Overstock</th>
                <th>Revenue at Risk</th>
                <th>Trapped Cost</th>
              </tr>
            </thead>

            <tbody>
              {
                warehouses.map(
                  (
                    row
                  ) => (
                    <tr
                      key={
                        row.warehouse
                      }
                    >
                      <td>
                        <strong>
                          {
                            row.warehouse
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          formatNumber(
                            row.skus
                          )
                        }
                      </td>

                      <td>
                        {
                          formatNumber(
                            row.closing_stock
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
                            row.inventory_cost_value
                          )
                        }
                      </td>

                      <td>
                        {
                          row.below_reorder_rows
                        }
                      </td>

                      <td>
                        {
                          row.overstock_rows
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row
                              .potential_revenue_at_risk
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row
                              .estimated_trapped_inventory_cost
                          )
                        }
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
            Category Inventory
          </h2>

          <p>
            Inventory exposure and stock risk
            by product category.
          </p>
        </div>
      </div>


      <div className="card">
        <div className="table-wrap">
          <table className="data-table">

            <thead>
              <tr>
                <th>Category</th>
                <th>SKUs</th>
                <th>Closing Stock</th>
                <th>Units Sold</th>
                <th>Inventory Cost</th>
                <th>Below Reorder</th>
                <th>Overstock</th>
                <th>Revenue at Risk</th>
                <th>Trapped Cost</th>
              </tr>
            </thead>

            <tbody>
              {
                categories.map(
                  (
                    row
                  ) => (
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
                            row.skus
                          )
                        }
                      </td>

                      <td>
                        {
                          formatNumber(
                            row.closing_stock
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
                            row.inventory_cost_value
                          )
                        }
                      </td>

                      <td>
                        {
                          row.below_reorder_rows
                        }
                      </td>

                      <td>
                        {
                          row.overstock_rows
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row
                              .potential_revenue_at_risk
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row
                              .estimated_trapped_inventory_cost
                          )
                        }
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
            SKU Inventory
          </h2>

          <p>
            Search for reorder candidates
            and excess-stock exposure.
          </p>
        </div>
      </div>


      <div className="card">

        <div className="filter-bar">

          <div className="search-control">
            <PackageSearch
              size={16}
            />

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
                  row
                ) => (
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


          <label className="checkbox-control">
            <input
              type="checkbox"
              checked={reorderOnly}
              onChange={
                (
                  event
                ) =>
                  setReorderOnly(
                    event.target.checked
                  )
              }
            />

            Reorder candidates only
          </label>

        </div>


        <div className="table-wrap">
          <table className="data-table">

            <thead>
              <tr>
                <th>Product</th>
                <th>Category</th>
                <th>Closing Stock</th>
                <th>Units Sold</th>
                <th>Reorder Point</th>
                <th>Below Reorder Locations</th>
                <th>Stock / Sales</th>
                <th>Revenue at Risk</th>
                <th>Trapped Cost</th>
              </tr>
            </thead>

            <tbody>
              {
                filteredSkus.map(
                  (
                    row
                  ) => (
                    <tr
                      key={
                        row.sku_id
                      }
                    >
                      <td>
                        <div>
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
                            row.closing_stock
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
                          formatNumber(
                            row.reorder_point
                          )
                        }
                      </td>

                      <td>
                        {
                          row
                            .below_reorder_locations
                        }
                      </td>

                      <td>
                        {
                          row
                            .stock_to_sales_ratio
                            .toFixed(2)
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row
                              .potential_revenue_at_risk
                          )
                        }
                      </td>

                      <td>
                        {
                          formatCurrency(
                            row
                              .estimated_trapped_inventory_cost
                          )
                        }
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
              filteredSkus.length
            )
          } of {
            formatNumber(
              skus.length
            )
          } SKUs
        </div>

      </div>


      <div className="card limitation-card">
        <div>
          <strong>
            Inventory scope
          </strong>

          <p>
            Inventory is currently a snapshot,
            not a dated historical series.
            Stock-to-sales ratio uses the period
            represented by the inventory dataset,
            so ProfitLens does not label it as
            days of inventory or days of cover.
            Overstock and trapped-capital metrics
            are deterministic heuristic signals.
          </p>
        </div>

        <Warehouse
          size={20}
        />
      </div>

    </div>
  )
}
import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowRight,
  Boxes,
  CircleDollarSign,
  PackageSearch,
  RefreshCcw,
  Search,
  Sparkles,
  TriangleAlert,
  Warehouse,
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
  D2CInventoryCategoryRow,
  D2CInventorySkuRow,
  D2CInventorySummaryResponse,
  D2CInventoryWarehouseRow,
} from '../types/api'

import type {
  MetricContract,
  MetricUnit,
} from '../types/metric'


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
  ).format(value)
}


function formatNumber(
  value: number
) {
  return new Intl.NumberFormat(
    'en-IN'
  ).format(value)
}


function buildMetric(
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


export default function Inventory() {
  const navigate =
    useNavigate()

  const drilldown =
    useMetricDrilldown()

  const [
    summary,
    setSummary,
  ] = useState<
    D2CInventorySummaryResponse | null
  >(null)

  const [
    skus,
    setSkus,
  ] = useState<
    D2CInventorySkuRow[]
  >([])

  const [
    warehouses,
    setWarehouses,
  ] = useState<
    D2CInventoryWarehouseRow[]
  >([])

  const [
    categories,
    setCategories,
  ] = useState<
    D2CInventoryCategoryRow[]
  >([])

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null)

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
      let cancelled =
        false

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
            if (
              cancelled
            ) {
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
          requestError => {
            if (
              cancelled
            ) {
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
                : (
                    'Could not load '
                    + 'inventory analytics.'
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
    []
  )


  const filteredSkus =
    useMemo(
      () => {
        const normalized =
          search
            .trim()
            .toLowerCase()

        return skus.filter(
          row => {
            const matchesSearch =
              !normalized
              || row.sku_id
                .toLowerCase()
                .includes(
                  normalized
                )
              || row.product_name
                .toLowerCase()
                .includes(
                  normalized
                )

            const matchesCategory =
              categoryFilter
              === 'All'
              || row.category
              === categoryFilter

            const matchesReorder =
              !reorderOnly
              || row
                .is_reorder_candidate

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


  const metrics =
    useMemo(
      () => {
        if (
          !summary
        ) {
          return []
        }

        return [
          buildMetric({
            metricId:
              'inventory_cost_value',

            label:
              'Inventory Cost Value',

            value:
              summary
                .inventory_cost_value,

            formattedValue:
              formatCurrency(
                summary
                  .inventory_cost_value
              ),

            unit:
              'currency',

            higherIsBetter:
              false,

            definition:
              'Current inventory valued at inventory cost.',
          }),

          buildMetric({
            metricId:
              'estimated_trapped_inventory_cost',

            label:
              'Trapped Inventory Cost',

            value:
              summary
                .estimated_trapped_inventory_cost,

            formattedValue:
              formatCurrency(
                summary
                  .estimated_trapped_inventory_cost
              ),

            unit:
              'currency',

            higherIsBetter:
              false,
          }),

          buildMetric({
            metricId:
              'potential_revenue_at_risk',

            label:
              'Revenue At Risk',

            value:
              summary
                .potential_revenue_at_risk,

            formattedValue:
              formatCurrency(
                summary
                  .potential_revenue_at_risk
              ),

            unit:
              'currency',

            higherIsBetter:
              false,
          }),

          buildMetric({
            metricId:
              'overstock_rows',

            label:
              'Overstock Positions',

            value:
              summary
                .overstock_rows,

            formattedValue:
              formatNumber(
                summary
                  .overstock_rows
              ),

            unit:
              'count',

            higherIsBetter:
              false,
          }),

          buildMetric({
            metricId:
              'slow_moving_rows',

            label:
              'Slow-Moving Positions',

            value:
              summary
                .slow_moving_rows,

            formattedValue:
              formatNumber(
                summary
                  .slow_moving_rows
              ),

            unit:
              'count',

            higherIsBetter:
              false,
          }),

          buildMetric({
            metricId:
              'below_reorder_rows',

            label:
              'Below Reorder Positions',

            value:
              summary
                .below_reorder_rows,

            formattedValue:
              formatNumber(
                summary
                  .below_reorder_rows
              ),

            unit:
              'count',

            higherIsBetter:
              false,
          }),
        ]
      },
      [
        summary,
      ]
    )


  const reorderPriorities =
    useMemo(
      () =>
        skus
          .filter(
            row =>
              row.is_reorder_candidate
          )
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second
                .potential_revenue_at_risk
              - first
                .potential_revenue_at_risk
          )
          .slice(
            0,
            6
          ),
      [
        skus,
      ]
    )


  const trappedCapitalSkus =
    useMemo(
      () =>
        skus
          .filter(
            row =>
              row
                .estimated_trapped_inventory_cost
              > 0
          )
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second
                .estimated_trapped_inventory_cost
              - first
                .estimated_trapped_inventory_cost
          )
          .slice(
            0,
            6
          ),
      [
        skus,
      ]
    )


  const categoryRisk =
    useMemo(
      () =>
        categories
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second
                .estimated_trapped_inventory_cost
              - first
                .estimated_trapped_inventory_cost
          ),
      [
        categories,
      ]
    )


  const warehouseRisk =
    useMemo(
      () =>
        warehouses
          .slice()
          .sort(
            (
              first,
              second,
            ) =>
              second
                .estimated_trapped_inventory_cost
              - first
                .estimated_trapped_inventory_cost
          ),
      [
        warehouses,
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
      <div className="pl-inventory-v2">

        <div className="pl-page-state">

          <RefreshCcw
            size={20}
          />

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
      <div className="pl-inventory-v2">

        <div className="pl-page-state error">

          <AlertTriangle
            size={20}
          />

          <div>

            <strong>
              Could not load inventory
            </strong>

            <span>
              {
                error
                ?? 'Inventory data is unavailable.'
              }
            </span>

          </div>

        </div>

      </div>
    )
  }


  return (
    <div className="pl-inventory-v2">

      <section className="pl-business-hero">

        <div>

          <div className="pl-page-eyebrow">
            Working capital intelligence
          </div>

          <h1>
            Inventory Performance
          </h1>

          <p>
            Identify trapped capital,
            replenishment risk and excess
            inventory across the current
            stock snapshot.
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

            Investigate inventory

            <ArrowRight
              size={14}
            />

          </button>

        </div>

      </section>


      <section className="pl-inventory-strip">

        <div>

          <Boxes
            size={17}
          />

          <span>
            Stock Units
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .total_closing_stock_units
              )
            }
          </strong>

        </div>


        <div>

          <PackageSearch
            size={17}
          />

          <span>
            Total SKUs
          </span>

          <strong>
            {
              formatNumber(
                summary.total_skus
              )
            }
          </strong>

        </div>


        <div>

          <Warehouse
            size={17}
          />

          <span>
            Warehouses
          </span>

          <strong>
            {
              formatNumber(
                summary.warehouses
              )
            }
          </strong>

        </div>


        <div>

          <CircleDollarSign
            size={17}
          />

          <span>
            Retail Value
          </span>

          <strong>
            {
              formatCompactCurrency(
                summary
                  .inventory_retail_value
              )
            }
          </strong>

        </div>

      </section>


      <section>

        <div className="pl-section-header">

          <div>

            <h2>
              Inventory health
            </h2>

            <p>
              Working-capital and availability
              risks from the current snapshot.
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


      <section className="pl-inventory-risk-strip">

        <div>

          <span>
            Low Stock
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .low_stock_rows
              )
            }
          </strong>

        </div>


        <div>

          <span>
            Out of Stock
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .out_of_stock_rows
              )
            }
          </strong>

        </div>


        <div>

          <span>
            SKU-Warehouse Positions
          </span>

          <strong>
            {
              formatNumber(
                summary
                  .sku_warehouse_rows
              )
            }
          </strong>

        </div>


        <div>

          <span>
            Coverage Basis
          </span>

          <strong>
            Stock / Sales
          </strong>

        </div>

      </section>


      <section className="pl-inventory-analysis-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Replenishment
              </span>

              <h2>
                Highest revenue-at-risk SKUs
              </h2>

            </div>

            <TriangleAlert
              size={18}
            />

          </div>


          <div className="pl-inventory-priority-list">

            {
              reorderPriorities.map(
                row => (
                  <div
                    key={
                      row.sku_id
                    }
                    className="pl-inventory-priority-row risk"
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
                        Revenue risk
                      </span>

                      <strong>
                        {
                          formatCurrency(
                            row
                              .potential_revenue_at_risk
                          )
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Coverage
                      </span>

                      <strong>
                        {
                          row
                            .stock_to_sales_ratio
                            .toFixed(2)
                        }x
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
                Working capital
              </span>

              <h2>
                Highest trapped-capital SKUs
              </h2>

            </div>

            <CircleDollarSign
              size={18}
            />

          </div>


          <div className="pl-inventory-priority-list">

            {
              trappedCapitalSkus.map(
                row => (
                  <div
                    key={
                      row.sku_id
                    }
                    className="pl-inventory-priority-row"
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
                        Trapped cost
                      </span>

                      <strong>
                        {
                          formatCurrency(
                            row
                              .estimated_trapped_inventory_cost
                          )
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Coverage
                      </span>

                      <strong>
                        {
                          row
                            .stock_to_sales_ratio
                            .toFixed(2)
                        }x
                      </strong>

                    </div>

                  </div>
                )
              )
            }

          </div>

        </div>

      </section>


      <section className="pl-inventory-analysis-grid">

        <div className="pl-founder-panel">

          <div className="pl-panel-header">

            <div>

              <span className="pl-page-eyebrow">
                Warehouse exposure
              </span>

              <h2>
                Working capital by warehouse
              </h2>

            </div>

          </div>


          <div className="pl-inventory-warehouse-list">

            {
              warehouseRisk.map(
                row => (
                  <div
                    key={
                      row.warehouse
                    }
                    className="pl-inventory-warehouse-row"
                  >

                    <strong>
                      {
                        row.warehouse
                      }
                    </strong>


                    <div>

                      <span>
                        Trapped
                      </span>

                      <strong>
                        {
                          formatCompactCurrency(
                            row
                              .estimated_trapped_inventory_cost
                          )
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Revenue Risk
                      </span>

                      <strong>
                        {
                          formatCompactCurrency(
                            row
                              .potential_revenue_at_risk
                          )
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Coverage
                      </span>

                      <strong>
                        {
                          row
                            .stock_to_sales_ratio
                            .toFixed(2)
                        }x
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
                Category exposure
              </span>

              <h2>
                Capital tied up by category
              </h2>

            </div>

          </div>


          <div className="pl-inventory-category-list">

            {
              categoryRisk.map(
                row => (
                  <div
                    key={
                      row.category
                    }
                    className="pl-inventory-category-row"
                  >

                    <strong>
                      {
                        row.category
                      }
                    </strong>


                    <div>

                      <span>
                        Trapped
                      </span>

                      <strong>
                        {
                          formatCompactCurrency(
                            row
                              .estimated_trapped_inventory_cost
                          )
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Overstock
                      </span>

                      <strong>
                        {
                          formatNumber(
                            row
                              .overstock_rows
                          )
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Coverage
                      </span>

                      <strong>
                        {
                          row
                            .stock_to_sales_ratio
                            .toFixed(2)
                        }x
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
              SKU control centre
            </span>

            <h2>
              Inventory priorities
            </h2>

          </div>


          <strong className="pl-inventory-result-count">
            {
              formatNumber(
                filteredSkus.length
              )
            } SKUs
          </strong>

        </div>


        <div className="pl-inventory-filters">

          <label className="pl-inventory-search">

            <Search
              size={15}
            />

            <input
              type="search"
              value={
                search
              }
              onChange={
                event =>
                  setSearch(
                    event.target.value
                  )
              }
              placeholder="Search SKU or product"
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
            aria-label="Inventory category"
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


          <label className="pl-inventory-toggle">

            <input
              type="checkbox"
              checked={
                reorderOnly
              }
              onChange={
                event =>
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
                <th>SKU</th>
                <th>Product</th>
                <th>Category</th>
                <th>Closing Stock</th>
                <th>Units Sold</th>
                <th>Coverage</th>
                <th>Revenue Risk</th>
                <th>Trapped Cost</th>
                <th>Reorder Locations</th>
                <th>Overstock Locations</th>
              </tr>

            </thead>


            <tbody>

              {
                filteredSkus.map(
                  row => (
                    <tr
                      key={
                        row.sku_id
                      }
                    >

                      <td>
                        <strong>
                          {
                            row.sku_id
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          row.product_name
                        }
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
                          row
                            .stock_to_sales_ratio
                            .toFixed(2)
                        }x
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

                      <td>
                        {
                          formatNumber(
                            row
                              .below_reorder_locations
                          )
                        }
                      </td>

                      <td>
                        {
                          formatNumber(
                            row
                              .overstock_locations
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

      </section>


      <section className="pl-inventory-scope-note">

        <Warehouse
          size={20}
        />

        <div>

          <strong>
            Current inventory snapshot
          </strong>

          <p>
            Inventory analytics currently
            represent a current stock snapshot.
            Historical inventory snapshots are
            not available, so ProfitLens does
            not display inventory trends or
            historical stock movement.
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

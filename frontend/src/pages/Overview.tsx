import {
  useEffect,
  useState,
} from 'react'

import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Boxes,
  CircleDollarSign,
  PackageCheck,
  Repeat2,
  RotateCcw,
  ShoppingCart,
  Target,
  Truck,
  Users,
  WalletCards,
} from 'lucide-react'

import {
  api,
} from '../api/profitlens'

import type {
  D2COverviewResponse,
} from '../types/api'


type OverviewProps = {
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


function GrowthIndicator({
  value,
}: {
  value: number
}) {
  const positive =
    value >= 0

  return (
    <span
      className={
        positive
          ? 'metric-growth positive'
          : 'metric-growth negative'
      }
    >
      {
        positive
          ? (
              <ArrowUpRight
                size={14}
              />
            )
          : (
              <ArrowDownRight
                size={14}
              />
            )
      }

      {Math.abs(value).toFixed(2)}%
    </span>
  )
}


function MetricCard({
  title,
  value,
  subtitle,
  icon,
  growth,
}: {
  title: string
  value: string
  subtitle?: string
  icon?: React.ReactNode
  growth?: number
}) {
  return (
    <div className="card metric-card">
      <div className="metric-card-top">
        <div>
          <div className="metric-label">
            {title}
          </div>

          <div className="metric-value">
            {value}
          </div>
        </div>

        {
          icon
          && (
            <div className="metric-icon">
              {icon}
            </div>
          )
        }
      </div>

      <div className="metric-footer">
        {
          growth !== undefined
          && (
            <GrowthIndicator
              value={growth}
            />
          )
        }

        {
          subtitle
          && (
            <span className="metric-subtitle">
              {subtitle}
            </span>
          )
        }
      </div>
    </div>
  )
}


function SectionTitle({
  title,
  description,
}: {
  title: string
  description?: string
}) {
  return (
    <div className="section-heading">
      <div>
        <h2>
          {title}
        </h2>

        {
          description
          && (
            <p>
              {description}
            </p>
          )
        }
      </div>
    </div>
  )
}


export default function Overview({
  month,
}: OverviewProps) {
  const [
    data,
    setData,
  ] = useState<
    D2COverviewResponse | null
  >(null)

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

  useEffect(
    () => {
      let cancelled = false

      setLoading(true)
      setError(null)

      api.overview(
        month
      )
        .then(
          (
            response
          ) => {
            if (!cancelled) {
              setData(
                response
              )
            }
          }
        )
        .catch(
          (
            requestError
          ) => {
            if (!cancelled) {
              setData(null)

              setError(
                requestError
                  instanceof Error
                  ? requestError.message
                  : 'Could not load ProfitLens overview.'
              )
            }
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

  if (loading) {
    return (
      <div className="page">
        <div className="card">
          <div className="loading-state">
            Loading ProfitLens overview...
          </div>
        </div>
      </div>
    )
  }

  if (
    error
    || !data
  ) {
    return (
      <div className="page">
        <div className="card error-card">
          <AlertTriangle
            size={20}
          />

          <div>
            <strong>
              Could not load data
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
    revenue,
    profitability,
    marketing,
    customers,
    logistics,
    products,
    inventory,
    reporting,
  } = data

  return (
    <div className="page">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div className="page-header">
        <div>
          <div className="eyebrow">
            Executive overview
          </div>

          <h2>
            Business Performance
          </h2>

          <p>
            Financial, customer, logistics,
            marketing and inventory performance
            for {month}.
          </p>
        </div>

        <div className="overview-period-badge">
          {month}
        </div>
      </div>


      {/* =====================================================
          PRIMARY KPIs
      ===================================================== */}

      <SectionTitle
        title="Business Health"
        description={
          'Core revenue and profitability metrics.'
        }
      />

      <div className="metric-grid">
        <MetricCard
          title="Realized Revenue"
          value={
            formatCurrency(
              revenue.realized_revenue
            )
          }
          growth={
            revenue.revenue_growth_percent
          }
          subtitle="vs previous month"
          icon={
            <CircleDollarSign
              size={20}
            />
          }
        />

        <MetricCard
          title="Orders"
          value={
            formatNumber(
              revenue.orders
            )
          }
          growth={
            revenue.order_growth_percent
          }
          subtitle="placed orders"
          icon={
            <ShoppingCart
              size={20}
            />
          }
        />

        <MetricCard
          title="AOV"
          value={
            formatCurrency(
              revenue.aov
            )
          }
          subtitle="realized revenue / orders"
          icon={
            <WalletCards
              size={20}
            />
          }
        />

        <MetricCard
          title="Contribution Profit"
          value={
            formatCurrency(
              profitability
                .contribution_profit_after_marketing
            )
          }
          growth={
            profitability
              .profit_after_marketing_growth_percent
          }
          subtitle="after marketing"
          icon={
            <Target
              size={20}
            />
          }
        />

        <MetricCard
          title="Contribution Margin"
          value={
            `${profitability
              .contribution_margin_after_marketing_percent
              .toFixed(2)}%`
          }
          subtitle="after marketing"
        />

        <MetricCard
          title="Gross Margin"
          value={
            `${profitability
              .gross_margin_percent
              .toFixed(2)}%`
          }
          subtitle={
            formatCurrency(
              profitability.gross_profit
            )
          }
        />
      </div>


      {/* =====================================================
          CUSTOMER + MARKETING
      ===================================================== */}

      <SectionTitle
        title="Growth & Customers"
        description={
          'Acquisition efficiency and customer quality.'
        }
      />

      <div className="metric-grid">
        <MetricCard
          title="Active Customers"
          value={
            formatNumber(
              customers.active_customers
            )
          }
          subtitle={
            `${formatNumber(
              customers.new_customers
            )} new`
          }
          icon={
            <Users
              size={20}
            />
          }
        />

        <MetricCard
          title="Repeat Customer Rate"
          value={
            `${customers
              .repeat_customer_rate_percent
              .toFixed(2)}%`
          }
          subtitle={
            `${formatNumber(
              customers.repeat_customers
            )} repeat customers`
          }
          icon={
            <Repeat2
              size={20}
            />
          }
        />

        <MetricCard
          title="ROAS"
          value={
            `${marketing
              .roas
              .toFixed(2)}x`
          }
          subtitle="attributed marketing ROAS"
          icon={
            <Target
              size={20}
            />
          }
        />

        <MetricCard
          title="CAC"
          value={
            formatCurrency(
              marketing.cac
            )
          }
          subtitle={
            `${formatNumber(
              marketing.new_customers
            )} attributed new customers`
          }
        />

        <MetricCard
          title="Marketing Spend"
          value={
            formatCurrency(
              marketing.marketing_spend
            )
          }
          subtitle={
            `${marketing
              .marketing_spend_percent_of_revenue
              .toFixed(2)}% of revenue`
          }
        />

        <MetricCard
          title="Attributed Revenue"
          value={
            formatCurrency(
              marketing.attributed_revenue
            )
          }
          subtitle={
            `${formatNumber(
              marketing.attributed_orders
            )} attributed orders`
          }
        />
      </div>


      {/* =====================================================
          LOGISTICS
      ===================================================== */}

      <SectionTitle
        title="Logistics Health"
        description={
          'Delivery performance, RTO and NDR risk.'
        }
      />

      <div className="metric-grid">
        <MetricCard
          title="Delivery Rate"
          value={
            `${logistics
              .delivery_rate_percent
              .toFixed(2)}%`
          }
          icon={
            <PackageCheck
              size={20}
            />
          }
        />

        <MetricCard
          title="RTO Rate"
          value={
            `${logistics
              .rto_rate_percent
              .toFixed(2)}%`
          }
          subtitle={
            `${formatNumber(
              logistics.rto_orders
            )} RTO orders`
          }
          icon={
            <RotateCcw
              size={20}
            />
          }
        />

        <MetricCard
          title="NDR Rate"
          value={
            `${logistics
              .ndr_rate_percent
              .toFixed(2)}%`
          }
          subtitle="non-delivery risk"
          icon={
            <AlertTriangle
              size={20}
            />
          }
        />

        <MetricCard
          title="On-Time Delivery"
          value={
            `${logistics
              .on_time_delivery_percent
              .toFixed(2)}%`
          }
          icon={
            <Truck
              size={20}
            />
          }
        />

        <MetricCard
          title="Average Delivery TAT"
          value={
            `${logistics
              .average_delivery_tat_days
              .toFixed(2)} days`
          }
        />

        <MetricCard
          title="P90 Delivery TAT"
          value={
            `${logistics
              .p90_delivery_tat_days
              .toFixed(2)} days`
          }
        />
      </div>


      {/* =====================================================
          PRODUCTS + INVENTORY
      ===================================================== */}

      <SectionTitle
        title="Products & Inventory"
        description={
          'Product concentration and working-capital risk.'
        }
      />

      <div className="metric-grid">
        <MetricCard
          title="Products"
          value={
            formatNumber(
              products.total_products
            )
          }
          subtitle={
            `${products.loss_making_products} loss-making`
          }
        />

        <MetricCard
          title="Top 10 Revenue Share"
          value={
            `${products
              .top_10_revenue_share_percent
              .toFixed(2)}%`
          }
          subtitle="product concentration"
        />

        <MetricCard
          title="Inventory at Cost"
          value={
            formatCurrency(
              inventory.inventory_cost_value
            )
          }
          subtitle={
            `${formatNumber(
              inventory.total_closing_stock_units
            )} units`
          }
          icon={
            <Boxes
              size={20}
            />
          }
        />

        <MetricCard
          title="Below Reorder"
          value={
            formatNumber(
              inventory.below_reorder_rows
            )
          }
          subtitle="SKU × warehouse positions"
        />

        <MetricCard
          title="Revenue at Risk"
          value={
            formatCurrency(
              inventory
                .potential_revenue_at_risk
            )
          }
          subtitle="reorder-gap estimate"
          icon={
            <AlertTriangle
              size={20}
            />
          }
        />

        <MetricCard
          title="Trapped Inventory"
          value={
            formatCurrency(
              inventory
                .estimated_trapped_inventory_cost
            )
          }
          subtitle="estimated excess stock at cost"
        />
      </div>


      {/* =====================================================
          PROFIT WATERFALL
      ===================================================== */}

      <SectionTitle
        title="Profitability Waterfall"
        description={
          'How revenue translates into contribution profit.'
        }
      />

      <div className="card">
        <div className="waterfall-list">

          <div className="waterfall-row">
            <span>
              Gross Product Revenue
            </span>

            <strong>
              {
                formatCurrency(
                  revenue
                    .gross_product_revenue
                )
              }
            </strong>
          </div>

          <div className="waterfall-row">
            <span>
              Net Product Revenue
            </span>

            <strong>
              {
                formatCurrency(
                  revenue
                    .net_product_revenue
                )
              }
            </strong>
          </div>

          <div className="waterfall-row">
            <span>
              Realized Revenue
            </span>

            <strong>
              {
                formatCurrency(
                  revenue
                    .realized_revenue
                )
              }
            </strong>
          </div>

          <div className="waterfall-row">
            <span>
              Gross Profit
            </span>

            <strong>
              {
                formatCurrency(
                  profitability
                    .gross_profit
                )
              }
            </strong>
          </div>

          <div className="waterfall-row">
            <span>
              Contribution Before Marketing
            </span>

            <strong>
              {
                formatCurrency(
                  profitability
                    .contribution_profit_before_marketing
                )
              }
            </strong>
          </div>

          <div className="waterfall-row negative-row">
            <span>
              Marketing Spend
            </span>

            <strong>
              -{
                formatCurrency(
                  profitability
                    .marketing_spend
                )
              }
            </strong>
          </div>

          <div className="waterfall-row final-row">
            <span>
              Contribution After Marketing
            </span>

            <strong>
              {
                formatCurrency(
                  profitability
                    .contribution_profit_after_marketing
                )
              }
            </strong>
          </div>

        </div>
      </div>


      {/* =====================================================
          DATA LIMITATIONS
      ===================================================== */}

      <div className="card limitation-card">
        <div>
          <strong>
            Data scope
          </strong>

          <p>
            Marketing attribution is currently
            {` ${marketing.attribution_level}`}.
            SKU-level contribution profit is not yet
            available because order-level variable
            costs require an allocation methodology.
            Inventory represents a {
              reporting.inventory_scope
            } rather than historical monthly inventory.
          </p>
        </div>
      </div>

    </div>
  )
}
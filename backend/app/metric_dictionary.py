from backend.app.metric_contracts import (
    MetricQuality,
    MetricUnit,
)


METRIC_DICTIONARY = {
    "realized_revenue": {
        "label": "Realized Revenue",
        "unit": MetricUnit.currency,
        "definition": (
            "Revenue recognized after removing "
            "non-realized order value such as failed "
            "or non-recognized outcomes."
        ),
        "formula": (
            "Recognized order revenue"
        ),
        "higher_is_better": True,
        "source_engine": (
            "d2c_financial_engine"
        ),
        "source_tables": [
            "orders",
            "order_items",
        ],
        "source_fields": [
            "order_id",
            "order_status",
            "selling_price",
            "quantity",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "orders": {
        "label": "Orders",
        "unit": MetricUnit.count,
        "definition": (
            "Total number of distinct orders "
            "observed in the selected period."
        ),
        "formula": (
            "COUNT DISTINCT order_id"
        ),
        "higher_is_better": True,
        "source_engine": (
            "d2c_financial_engine"
        ),
        "source_tables": [
            "orders",
        ],
        "source_fields": [
            "order_id",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "aov": {
        "label": "Average Order Value",
        "unit": MetricUnit.currency,
        "definition": (
            "Average realized revenue generated "
            "per order."
        ),
        "formula": (
            "Realized Revenue / Orders"
        ),
        "higher_is_better": True,
        "source_engine": (
            "d2c_financial_engine"
        ),
        "source_tables": [
            "orders",
            "order_items",
        ],
        "source_fields": [
            "order_id",
            "selling_price",
            "quantity",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "contribution_profit_after_marketing": {
        "label": "Contribution Profit",
        "unit": MetricUnit.currency,
        "definition": (
            "Profit remaining after recognized "
            "variable operating costs and marketing spend."
        ),
        "formula": (
            "Realized Revenue "
            "- Recognized COGS "
            "- Forward Shipping "
            "- COD Fees "
            "- Payment Fees "
            "- RTO Costs "
            "- Marketing Spend"
        ),
        "higher_is_better": True,
        "source_engine": (
            "d2c_profitability_engine"
        ),
        "source_tables": [
            "orders",
            "order_items",
            "payments",
            "marketing",
            "couriers",
        ],
        "source_fields": [
            "selling_price",
            "quantity",
            "cogs",
            "shipping_cost",
            "payment_fee",
            "marketing_spend",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [
            (
                "Marketing spend may be allocated "
                "at aggregate period level when "
                "order-level attribution is unavailable."
            )
        ],
    },

    "contribution_margin_after_marketing_percent": {
        "label": "Contribution Margin",
        "unit": MetricUnit.percent,
        "definition": (
            "Contribution profit expressed as a "
            "percentage of realized revenue."
        ),
        "formula": (
            "Contribution Profit / "
            "Realized Revenue * 100"
        ),
        "higher_is_better": True,
        "source_engine": (
            "d2c_profitability_engine"
        ),
        "source_tables": [
            "orders",
            "order_items",
            "payments",
            "marketing",
            "couriers",
        ],
        "source_fields": [],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "marketing_spend": {
        "label": "Marketing Spend",
        "unit": MetricUnit.currency,
        "definition": (
            "Total paid marketing spend "
            "recorded for the selected period."
        ),
        "formula": (
            "SUM marketing spend"
        ),
        "higher_is_better": None,
        "source_engine": (
            "d2c_marketing_engine"
        ),
        "source_tables": [
            "marketing",
        ],
        "source_fields": [
            "spend",
            "channel",
            "campaign",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "blended_roas": {
        "label": "Blended ROAS",
        "unit": MetricUnit.ratio,
        "definition": (
            "Attributed revenue divided by "
            "total marketing spend."
        ),
        "formula": (
            "Attributed Revenue / Marketing Spend"
        ),
        "higher_is_better": True,
        "source_engine": (
            "d2c_marketing_engine"
        ),
        "source_tables": [
            "marketing",
        ],
        "source_fields": [
            "spend",
            "attributed_revenue",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [
            (
                "Attributed revenue is based on "
                "available marketing attribution data."
            )
        ],
    },

    "cac": {
        "label": "Customer Acquisition Cost",
        "unit": MetricUnit.currency,
        "definition": (
            "Marketing spend divided by "
            "new customers acquired."
        ),
        "formula": (
            "Marketing Spend / New Customers"
        ),
        "higher_is_better": False,
        "source_engine": (
            "d2c_marketing_engine"
        ),
        "source_tables": [
            "marketing",
            "customers",
        ],
        "source_fields": [
            "spend",
            "new_customers",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "repeat_customer_rate_percent": {
        "label": "Repeat Customer Rate",
        "unit": MetricUnit.percent,
        "definition": (
            "Share of active customers who "
            "have purchased previously."
        ),
        "formula": (
            "Repeat Customers / "
            "Active Customers * 100"
        ),
        "higher_is_better": True,
        "source_engine": (
            "d2c_customer_engine"
        ),
        "source_tables": [
            "orders",
            "customers",
        ],
        "source_fields": [
            "customer_id",
            "order_date",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "rto_rate_percent": {
        "label": "RTO Rate",
        "unit": MetricUnit.percent,
        "definition": (
            "Share of orders returned to origin."
        ),
        "formula": (
            "RTO Orders / Total Orders * 100"
        ),
        "higher_is_better": False,
        "source_engine": (
            "d2c_logistics_engine"
        ),
        "source_tables": [
            "orders",
        ],
        "source_fields": [
            "order_id",
            "order_status",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "ndr_rate_percent": {
        "label": "NDR Rate",
        "unit": MetricUnit.percent,
        "definition": (
            "Share of orders entering "
            "non-delivery report status."
        ),
        "formula": (
            "NDR Orders / Total Orders * 100"
        ),
        "higher_is_better": False,
        "source_engine": (
            "d2c_logistics_engine"
        ),
        "source_tables": [
            "orders",
        ],
        "source_fields": [
            "order_id",
            "ndr_flag",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "average_delivery_tat_days": {
        "label": "Average Delivery TAT",
        "unit": MetricUnit.days,
        "definition": (
            "Average time between shipment "
            "creation and customer delivery."
        ),
        "formula": (
            "AVG delivery_date - order/shipment start date"
        ),
        "higher_is_better": False,
        "source_engine": (
            "d2c_logistics_engine"
        ),
        "source_tables": [
            "orders",
        ],
        "source_fields": [
            "order_date",
            "delivery_date",
        ],
        "grain": "brand_period",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "inventory_cost_value": {
        "label": "Inventory Cost Value",
        "unit": MetricUnit.currency,
        "definition": (
            "Estimated cost value of current "
            "inventory holdings."
        ),
        "formula": (
            "SUM current stock * unit cost"
        ),
        "higher_is_better": None,
        "source_engine": (
            "d2c_inventory_engine"
        ),
        "source_tables": [
            "inventory",
            "products",
        ],
        "source_fields": [
            "stock",
            "unit_cost",
            "sku",
        ],
        "grain": "brand_snapshot",
        "data_quality": (
            MetricQuality.verified
        ),
        "limitations": [],
    },

    "estimated_trapped_inventory_cost": {
        "label": "Trapped Inventory Cost",
        "unit": MetricUnit.currency,
        "definition": (
            "Estimated working capital tied up "
            "in excess or slow-moving stock."
        ),
        "formula": (
            "Estimated excess units * unit cost"
        ),
        "higher_is_better": False,
        "source_engine": (
            "d2c_inventory_engine"
        ),
        "source_tables": [
            "inventory",
            "products",
        ],
        "source_fields": [
            "stock",
            "sales_velocity",
            "unit_cost",
        ],
        "grain": "brand_snapshot",
        "data_quality": (
            MetricQuality.estimated
        ),
        "limitations": [
            (
                "Trapped inventory is an operational "
                "estimate based on observed stock "
                "and movement thresholds."
            )
        ],
    },
}

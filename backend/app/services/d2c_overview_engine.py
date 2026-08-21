from backend.app.services.d2c_financial_engine import (
    get_d2c_financial_summary,
)
from backend.app.services.d2c_profitability_engine import (
    get_profitability_summary,
)
from backend.app.services.d2c_product_engine import (
    get_product_summary,
)
from backend.app.services.d2c_customer_engine import (
    get_customer_summary,
)
from backend.app.services.d2c_logistics_engine import (
    get_logistics_summary,
)
from backend.app.services.d2c_inventory_engine import (
    get_inventory_summary,
)


def get_d2c_overview(month: str):
    """
    Build the canonical executive D2C overview.

    All business calculations remain inside their
    respective deterministic engines.

    This layer only combines already-calculated metrics.
    """

    financials = get_d2c_financial_summary(month)
    profitability = get_profitability_summary(month)
    products = get_product_summary(month)
    customers = get_customer_summary(month)
    logistics = get_logistics_summary(month)
    inventory = get_inventory_summary()

    return {
        "month": month,

        "reporting": {
            "inventory_scope": inventory[
                "inventory_scope"
            ],
            "historical_inventory_available": inventory[
                "historical_inventory_available"
            ],
        },

        "revenue": {
            "orders": financials["orders"],
            "gross_product_revenue": financials[
                "gross_product_revenue"
            ],
            "net_product_revenue": financials[
                "net_product_revenue"
            ],
            "realized_revenue": financials[
                "realized_revenue"
            ],
            "aov": financials["aov"],
            "revenue_growth_percent": financials[
                "revenue_growth_percent"
            ],
            "order_growth_percent": financials[
                "order_growth_percent"
            ],
        },

        "profitability": {
            "gross_profit": financials[
                "gross_profit"
            ],
            "gross_margin_percent": financials[
                "gross_margin_percent"
            ],
            "contribution_profit_before_marketing": (
                profitability[
                    "contribution_profit_before_marketing"
                ]
            ),
            "contribution_margin_before_marketing_percent": (
                profitability[
                    "contribution_margin_before_marketing_percent"
                ]
            ),
            "marketing_spend": profitability[
                "marketing_spend"
            ],
            "contribution_profit_after_marketing": (
                profitability[
                    "contribution_profit_after_marketing"
                ]
            ),
            "contribution_margin_after_marketing_percent": (
                profitability[
                    "contribution_margin_after_marketing_percent"
                ]
            ),
            "profit_after_marketing_growth_percent": (
                profitability[
                    "profit_after_marketing_growth_percent"
                ]
            ),
        },

        "marketing": {
            "marketing_spend": profitability[
                "marketing_spend"
            ],
            "attributed_revenue": profitability[
                "attributed_revenue"
            ],
            "roas": profitability["roas"],
            "cac": profitability["cac"],
            "attributed_orders": profitability[
                "attributed_orders"
            ],
            "new_customers": profitability[
                "new_customers"
            ],
            "cost_per_attributed_order": profitability[
                "cost_per_attributed_order"
            ],
            "session_conversion_percent": profitability[
                "session_conversion_percent"
            ],
            "marketing_spend_percent_of_revenue": (
                profitability[
                    "marketing_spend_percent_of_revenue"
                ]
            ),
            "attribution_level": profitability[
                "marketing_attribution_level"
            ],
        },

        "customers": {
            "active_customers": customers[
                "active_customers"
            ],
            "new_customers": customers[
                "new_customers"
            ],
            "repeat_customers": customers[
                "repeat_customers"
            ],
            "repeat_customer_rate_percent": customers[
                "repeat_customer_rate_percent"
            ],
            "orders_per_customer": customers[
                "orders_per_customer"
            ],
            "cod_share_percent": customers[
                "cod_share_percent"
            ],
        },

        "logistics": {
            "delivery_rate_percent": logistics[
                "delivery_rate_percent"
            ],
            "rto_orders": logistics[
                "rto_orders"
            ],
            "rto_rate_percent": logistics[
                "rto_rate_percent"
            ],
            "return_rate_percent": logistics[
                "return_rate_percent"
            ],
            "ndr_rate_percent": logistics[
                "ndr_rate_percent"
            ],
            "average_delivery_tat_days": logistics[
                "average_delivery_tat_days"
            ],
            "p90_delivery_tat_days": logistics[
                "p90_delivery_tat_days"
            ],
            "on_time_delivery_percent": logistics[
                "on_time_delivery_percent"
            ],
        },

        "products": {
            "total_products": products[
                "total_products"
            ],
            "loss_making_products": products[
                "loss_making_products"
            ],
            "top_5_revenue_share_percent": products[
                "top_5_revenue_share_percent"
            ],
            "top_10_revenue_share_percent": products[
                "top_10_revenue_share_percent"
            ],
            "profitability_level": products[
                "profitability_level"
            ],
        },

        "inventory": {
            "total_skus": inventory[
                "total_skus"
            ],
            "warehouses": inventory[
                "warehouses"
            ],
            "total_closing_stock_units": inventory[
                "total_closing_stock_units"
            ],
            "inventory_cost_value": inventory[
                "inventory_cost_value"
            ],
            "below_reorder_rows": inventory[
                "below_reorder_rows"
            ],
            "out_of_stock_rows": inventory[
                "out_of_stock_rows"
            ],
            "overstock_rows": inventory[
                "overstock_rows"
            ],
            "slow_moving_rows": inventory[
                "slow_moving_rows"
            ],
            "potential_revenue_at_risk": inventory[
                "potential_revenue_at_risk"
            ],
            "estimated_trapped_inventory_cost": inventory[
                "estimated_trapped_inventory_cost"
            ],
        },

        "limitations": {
            "marketing_attribution_level": profitability[
                "marketing_attribution_level"
            ],
            "order_level_marketing_allocation_available": (
                profitability[
                    "order_level_marketing_allocation_available"
                ]
            ),
            "sku_contribution_profit_available": products[
                "sku_contribution_profit_available"
            ],
            "historical_inventory_available": inventory[
                "historical_inventory_available"
            ],
        },
    }
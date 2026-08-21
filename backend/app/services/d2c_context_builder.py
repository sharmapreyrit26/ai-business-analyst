from backend.app.services.d2c_overview_engine import (
    get_d2c_overview,
)

from backend.app.services.d2c_product_engine import (
    get_product_summary,
    get_category_performance,
)

from backend.app.services.d2c_customer_engine import (
    get_customer_summary,
    get_acquisition_channel_performance,
)

from backend.app.services.d2c_logistics_engine import (
    get_logistics_summary,
    get_courier_performance,
    get_payment_logistics_performance,
    get_zone_performance,
)

from backend.app.services.d2c_inventory_engine import (
    get_inventory_summary,
    get_sku_inventory_performance,
)

from backend.app.services.d2c_marketing_engine import (
    get_marketing_summary,
    get_channel_performance,
    get_marketing_insights,
)


def build_d2c_business_context(
    month: str,
):
    """
    Build deterministic business context for the
    ProfitLens AI analyst.

    The LLM may interpret these results but must not
    independently calculate financial truth.
    """

    overview = (
        get_d2c_overview(
            month
        )
    )

    products = (
        get_product_summary(
            month
        )
    )

    categories = (
        get_category_performance(
            month
        )
    )

    customers = (
        get_customer_summary(
            month
        )
    )

    acquisition = (
        get_acquisition_channel_performance(
            month
        )
    )

    logistics = (
        get_logistics_summary(
            month
        )
    )

    couriers = (
        get_courier_performance(
            month
        )
    )

    payment_logistics = (
        get_payment_logistics_performance(
            month
        )
    )

    zones = (
        get_zone_performance(
            month
        )
    )

    inventory = (
        get_inventory_summary()
    )

    inventory_skus = (
        get_sku_inventory_performance()
    )

    marketing = (
        get_marketing_summary(
            month
        )
    )

    marketing_channels = (
        get_channel_performance(
            month
        )
    )

    marketing_insights = (
        get_marketing_insights(
            month
        )
    )

    return {
        "month": month,

        "overview": overview,

        "products": {
            "summary": products,
            "categories": (
                categories
                .to_dict(
                    orient="records"
                )
            ),
        },

        "customers": {
            "summary": customers,
            "acquisition_channels": (
                acquisition
                .to_dict(
                    orient="records"
                )
            ),
        },

        "logistics": {
            "summary": logistics,
            "couriers": (
                couriers
                .to_dict(
                    orient="records"
                )
            ),
            "payment_logistics": (
                payment_logistics
                .to_dict(
                    orient="records"
                )
            ),
            "zones": (
                zones
                .to_dict(
                    orient="records"
                )
            ),
        },

        "inventory": {
            "summary": inventory,

            # Only top operational risks should be
            # passed into the LLM context.
            "reorder_candidates": (
                inventory_skus[
                    inventory_skus[
                        "is_reorder_candidate"
                    ]
                ]
                .head(20)
                .to_dict(
                    orient="records"
                )
            ),

            "highest_trapped_inventory": (
                inventory_skus
                .sort_values(
                    "estimated_trapped_inventory_cost",
                    ascending=False,
                )
                .head(20)
                .to_dict(
                    orient="records"
                )
            ),
        },

        "marketing": {
            "summary": marketing,
            "channels": (
                marketing_channels
                .to_dict(
                    orient="records"
                )
            ),
            "insights": (
                marketing_insights
            ),
        },

        "rules": {
            "financial_truth_source": (
                "deterministic_python_engines"
            ),
            "llm_may_calculate_financial_truth": (
                False
            ),
            "inventory_scope": (
                "current_snapshot"
            ),
            "marketing_attribution_level": (
                overview[
                    "limitations"
                ][
                    "marketing_attribution_level"
                ]
            ),
        },
    }
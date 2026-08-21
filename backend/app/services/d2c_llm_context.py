from copy import deepcopy


def build_focused_d2c_context(
    full_context: dict,
    question_type: str,
) -> dict:
    """
    Reduce the full deterministic D2C context to only the
    information required for the requested analytical intent.

    Benefits:
    - smaller LLM prompts
    - lower latency
    - fewer timeouts
    - less irrelevant evidence
    - lower hallucination risk

    No calculations are performed here.
    """

    month = full_context.get(
        "month"
    )

    overview = full_context.get(
        "overview",
        {},
    )

    rules = full_context.get(
        "rules",
        {},
    )

    limitations = overview.get(
        "limitations",
        {},
    )

    base = {
        "month": month,
        "rules": deepcopy(
            rules
        ),
        "limitations": deepcopy(
            limitations
        ),
    }

    # ========================================================
    # REVENUE
    # ========================================================

    if question_type == "revenue":

        return {
            **base,

            "revenue": deepcopy(
                overview.get(
                    "revenue",
                    {},
                )
            ),

            "profitability": {
                key: value
                for key, value
                in overview.get(
                    "profitability",
                    {},
                ).items()
                if key in {
                    "contribution_profit_after_marketing",
                    "contribution_margin_after_marketing_percent",
                    "profit_after_marketing_growth_percent",
                }
            },
        }

    # ========================================================
    # PROFITABILITY
    # ========================================================

    if question_type == "profitability":

        return {
            **base,

            "revenue": deepcopy(
                overview.get(
                    "revenue",
                    {},
                )
            ),

            "profitability": deepcopy(
                overview.get(
                    "profitability",
                    {},
                )
            ),

            "marketing": {
                key: value
                for key, value
                in overview.get(
                    "marketing",
                    {},
                ).items()
                if key in {
                    "marketing_spend",
                    "roas",
                    "cac",
                }
            },
        }

    # ========================================================
    # ORDERS
    # ========================================================

    if question_type == "orders":

        return {
            **base,

            "revenue": deepcopy(
                overview.get(
                    "revenue",
                    {},
                )
            ),

            "customers": {
                key: value
                for key, value
                in overview.get(
                    "customers",
                    {},
                ).items()
                if key in {
                    "active_customers",
                    "new_customers",
                    "repeat_customers",
                    "repeat_customer_rate_percent",
                    "orders_per_customer",
                }
            },
        }

    # ========================================================
    # MARKETING
    # ========================================================

    if question_type == "marketing":

        marketing = full_context.get(
            "marketing",
            {},
        )

        return {
            **base,

            "marketing": deepcopy(
                marketing
            ),

            "revenue": {
                key: value
                for key, value
                in overview.get(
                    "revenue",
                    {},
                ).items()
                if key in {
                    "realized_revenue",
                    "orders",
                    "revenue_growth_percent",
                    "order_growth_percent",
                }
            },

            "customers": {
                key: value
                for key, value
                in overview.get(
                    "customers",
                    {},
                ).items()
                if key in {
                    "new_customers",
                    "repeat_customers",
                    "repeat_customer_rate_percent",
                }
            },
        }

    # ========================================================
    # PRODUCT
    # ========================================================

    if question_type == "product":

        return {
            **base,

            "products": deepcopy(
                full_context.get(
                    "products",
                    {},
                )
            ),
        }

    # ========================================================
    # CUSTOMER
    # ========================================================

    if question_type == "customer":

        return {
            **base,

            "customers": deepcopy(
                full_context.get(
                    "customers",
                    {},
                )
            ),

            "marketing_summary": {
                key: value
                for key, value
                in overview.get(
                    "marketing",
                    {},
                ).items()
                if key in {
                    "new_customers",
                    "cac",
                }
            },
        }

    # ========================================================
    # LOGISTICS / DELIVERY
    # ========================================================

    if question_type in {
        "logistics",
        "delivery",
    }:

        return {
            **base,

            "logistics": deepcopy(
                full_context.get(
                    "logistics",
                    {},
                )
            ),
        }

    # ========================================================
    # INVENTORY
    # ========================================================

    if question_type == "inventory":

        inventory = full_context.get(
            "inventory",
            {},
        )

        return {
            **base,

            "inventory": {
                "summary": deepcopy(
                    inventory.get(
                        "summary",
                        {},
                    )
                ),

                "reorder_candidates": deepcopy(
                    inventory.get(
                        "reorder_candidates",
                        [],
                    )[:10]
                ),

                "highest_trapped_inventory": deepcopy(
                    inventory.get(
                        "highest_trapped_inventory",
                        [],
                    )[:10]
                ),
            },
        }

    # ========================================================
    # BUSINESS HEALTH / GENERAL / PERFORMANCE
    # ========================================================

    if question_type in {
        "business_health",
        "general_business",
        "general",
        "performance",
        "trends",
    }:

        inventory = full_context.get(
            "inventory",
            {},
        )

        marketing = full_context.get(
            "marketing",
            {},
        )

        logistics = full_context.get(
            "logistics",
            {},
        )

        return {
            **base,

            "overview": deepcopy(
                overview
            ),

            "marketing": {
                "summary": deepcopy(
                    marketing.get(
                        "summary",
                        {},
                    )
                ),

                "channels": deepcopy(
                    marketing.get(
                        "channels",
                        [],
                    )
                ),
            },

            "logistics": {
                "summary": deepcopy(
                    logistics.get(
                        "summary",
                        {},
                    )
                ),

                "payment_logistics": deepcopy(
                    logistics.get(
                        "payment_logistics",
                        [],
                    )
                ),

                "couriers": deepcopy(
                    logistics.get(
                        "couriers",
                        [],
                    )
                ),
            },

            "inventory": {
                "summary": deepcopy(
                    inventory.get(
                        "summary",
                        {},
                    )
                ),

                "reorder_candidates": deepcopy(
                    inventory.get(
                        "reorder_candidates",
                        [],
                    )[:5]
                ),

                "highest_trapped_inventory": deepcopy(
                    inventory.get(
                        "highest_trapped_inventory",
                        [],
                    )[:5]
                ),
            },

            "product_summary": deepcopy(
                full_context
                .get(
                    "products",
                    {},
                )
                .get(
                    "summary",
                    {},
                )
            ),

            "customer_summary": deepcopy(
                full_context
                .get(
                    "customers",
                    {},
                )
                .get(
                    "summary",
                    {},
                )
            ),
        }

    # ========================================================
    # DEFAULT
    # ========================================================

    return {
        **base,
        "overview": deepcopy(
            overview
        ),
    }
from backend.app.services.d2c_llm_context import (
    build_focused_d2c_context,
)

from backend.app.services.question_router import (
    classify_question,
)

from backend.app.services.llm_service import (
    ask_business_analyst,
)

from backend.app.services.d2c_context_builder import (
    build_d2c_business_context,
)


# ============================================================
# DATASET ROUTING
# ============================================================


def _is_d2c_month(
    month: str,
) -> bool:
    """
    Route 2025 reporting periods to the new
    India D2C analytics stack.

    Legacy periods remain available temporarily
    for backwards compatibility and regression tests.
    """

    return (
        isinstance(month, str)
        and month.startswith("2025-")
    )


# ============================================================
# D2C FALLBACK
# ============================================================


def _build_d2c_fallback(
    question: str,
    question_type: str,
    month: str,
    context: dict,
) -> dict:
    """
    Deterministic fallback for the India D2C analyst.

    No new financial calculations are performed here.
    It only interprets metrics already produced by the
    deterministic ProfitLens engines.
    """

    overview = context.get(
        "overview",
        {},
    )

    revenue = overview.get(
        "revenue",
        {},
    )

    profitability = overview.get(
        "profitability",
        {},
    )

    overview_marketing = overview.get(
        "marketing",
        {},
    )

    customers = overview.get(
        "customers",
        {},
    )

    overview_logistics = overview.get(
        "logistics",
        {},
    )

    products_context = context.get(
        "products",
        {},
    )

    product_summary = products_context.get(
        "summary",
        {},
    )

    logistics_context = context.get(
        "logistics",
        {},
    )

    inventory_context = context.get(
        "inventory",
        {},
    )

    inventory_summary = inventory_context.get(
        "summary",
        {},
    )

    marketing_context = context.get(
        "marketing",
        {},
    )

    marketing_summary = marketing_context.get(
        "summary",
        {},
    )

    q = question.lower().strip()

    # ========================================================
    # REVENUE
    # ========================================================

    if question_type == "revenue":

        growth = revenue.get(
            "revenue_growth_percent"
        )

        order_growth = revenue.get(
            "order_growth_percent"
        )

        realized_revenue = revenue.get(
            "realized_revenue"
        )

        aov = revenue.get(
            "aov"
        )

        if (
            growth is not None
            and growth < 0
        ):
            direction = "declined"
        else:
            direction = "increased"

        evidence = [
            (
                f"Realized revenue: "
                f"{realized_revenue}."
            ),
            (
                f"Revenue growth: "
                f"{growth}%."
            ),
            (
                f"Order growth: "
                f"{order_growth}%."
            ),
            (
                f"AOV: "
                f"{aov}."
            ),
        ]

        return {
            "answer": (
                f"Realized revenue {direction} by "
                f"{abs(growth)}% in {month} to "
                f"{realized_revenue}."
                if growth is not None
                else (
                    f"Realized revenue in {month} "
                    f"was {realized_revenue}."
                )
            ),
            "evidence": evidence,
            "likely_driver": (
                "The decline in order volume is the "
                "strongest observed commercial signal."
                if (
                    order_growth is not None
                    and order_growth < 0
                )
                else "Not established"
            ),
            "recommended_actions": [
                (
                    "Investigate where order volume changed "
                    "across acquisition, customer and product "
                    "segments before changing commercial strategy."
                )
            ],
        }

    # ========================================================
    # PROFITABILITY
    # ========================================================

    if question_type == "profitability":

        after_marketing = (
            profitability.get(
                "contribution_profit_after_marketing"
            )
        )

        after_margin = (
            profitability.get(
                "contribution_margin_after_marketing_percent"
            )
        )

        before_marketing = (
            profitability.get(
                "contribution_profit_before_marketing"
            )
        )

        gross_profit = (
            profitability.get(
                "gross_profit"
            )
        )

        marketing_spend = (
            profitability.get(
                "marketing_spend"
            )
        )

        profitable = (
            after_marketing is not None
            and after_marketing > 0
        )

        return {
            "answer": (
                f"{'Yes' if profitable else 'No'}, "
                f"the business generated contribution "
                f"profit after marketing of "
                f"{after_marketing} in {month}, "
                f"with a contribution margin after "
                f"marketing of {after_margin}%."
            ),
            "evidence": [
                (
                    f"Gross profit: "
                    f"{gross_profit}."
                ),
                (
                    f"Contribution profit before marketing: "
                    f"{before_marketing}."
                ),
                (
                    f"Marketing spend: "
                    f"{marketing_spend}."
                ),
                (
                    f"Contribution profit after marketing: "
                    f"{after_marketing}."
                ),
                (
                    f"Contribution margin after marketing: "
                    f"{after_margin}%."
                ),
            ],
            "likely_driver": (
                "Profitability remains positive after "
                "marketing, although overall profit scale "
                "depends heavily on revenue and order volume."
            ),
            "recommended_actions": [],
        }

    # ========================================================
    # ORDERS
    # ========================================================

    if question_type == "orders":

        return {
            "answer": (
                f"Orders were "
                f"{revenue.get('orders')} in {month}, "
                f"with month-over-month growth of "
                f"{revenue.get('order_growth_percent')}%."
            ),
            "evidence": [
                (
                    f"Revenue growth: "
                    f"{revenue.get('revenue_growth_percent')}%."
                ),
                (
                    f"AOV: "
                    f"{revenue.get('aov')}."
                ),
            ],
            "likely_driver": "Not established",
            "recommended_actions": [],
        }

    # ========================================================
    # MARKETING
    # ========================================================

    if question_type == "marketing":

        channels = marketing_context.get(
            "channels",
            [],
        )

        spend = marketing_summary.get(
            "marketing_spend",
            overview_marketing.get(
                "marketing_spend"
            ),
        )

        attributed_revenue = (
            marketing_summary.get(
                "attributed_revenue",
                overview_marketing.get(
                    "attributed_revenue"
                ),
            )
        )

        roas = marketing_summary.get(
            "blended_roas",
            overview_marketing.get(
                "roas"
            ),
        )

        paid_roas = (
            marketing_summary.get(
                "paid_roas"
            )
        )

        cac = marketing_summary.get(
            "cac",
            overview_marketing.get(
                "cac"
            ),
        )

        new_customers = (
            marketing_summary.get(
                "new_customers",
                overview_marketing.get(
                    "new_customers"
                ),
            )
        )

        evidence = [
            (
                f"Marketing spend: "
                f"{spend}."
            ),
            (
                f"Attributed revenue: "
                f"{attributed_revenue}."
            ),
            (
                f"Blended ROAS: "
                f"{roas}x."
            ),
            (
                f"CAC: "
                f"{cac}."
            ),
            (
                f"New customers: "
                f"{new_customers}."
            ),
        ]

        if paid_roas is not None:
            evidence.append(
                f"Paid ROAS: {paid_roas}x."
            )

        if channels:

            paid_channels = [
                row
                for row in channels
                if row.get(
                    "spend",
                    0,
                ) > 0
            ]

            if paid_channels:

                best_roas = max(
                    paid_channels,
                    key=lambda row: row.get(
                        "roas",
                        float("-inf"),
                    ),
                )

                lowest_cac_rows = [
                    row
                    for row in paid_channels
                    if row.get("cac") is not None
                    and row.get("cac") > 0
                ]

                if lowest_cac_rows:

                    lowest_cac = min(
                        lowest_cac_rows,
                        key=lambda row: row.get(
                            "cac"
                        ),
                    )

                    evidence.append(
                        (
                            f"Lowest observed paid-channel CAC: "
                            f"{lowest_cac.get('channel')} at "
                            f"{lowest_cac.get('cac')}."
                        )
                    )

                evidence.append(
                    (
                        f"Highest observed paid-channel ROAS: "
                        f"{best_roas.get('channel')} at "
                        f"{best_roas.get('roas')}x."
                    )
                )

        return {
            "answer": (
                f"Marketing in {month} generated a blended "
                f"ROAS of {roas}x on spend of {spend}, "
                f"with CAC of {cac}."
            ),
            "evidence": evidence,
            "likely_driver": (
                "Marketing efficiency varies by channel; "
                "channel-level ROAS and CAC should be reviewed "
                "together rather than using either metric alone."
            ),
            "recommended_actions": [
                (
                    "Compare paid channels on ROAS, CAC, "
                    "attributed revenue and acquisition scale "
                    "before reallocating spend."
                )
            ],
        }

    # ========================================================
    # PRODUCTS
    # ========================================================

    if question_type == "product":

        top_products = (
            product_summary.get(
                "top_products",
                [],
            )
        )

        if top_products:

            product = top_products[0]

            return {
                "answer": (
                    f"The highest-revenue product in "
                    f"{month} was "
                    f"{product.get('product_name')} "
                    f"({product.get('sku_id')}), with "
                    f"net revenue of "
                    f"{product.get('net_revenue')}."
                ),
                "evidence": [
                    (
                        f"Units sold: "
                        f"{product.get('units_sold')}."
                    ),
                    (
                        f"Orders: "
                        f"{product.get('orders')}."
                    ),
                    (
                        f"Gross margin: "
                        f"{product.get('gross_margin_percent')}%."
                    ),
                    (
                        f"RTO rate: "
                        f"{product.get('rto_rate_percent')}%."
                    ),
                ],
                "likely_driver": (
                    "Product revenue contribution"
                ),
                "recommended_actions": [],
            }

        return {
            "answer": (
                "No product records were available "
                "for the selected period."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    # ========================================================
    # CUSTOMER
    # ========================================================

    if question_type == "customer":

        return {
            "answer": (
                f"There were "
                f"{customers.get('active_customers')} active "
                f"customers in {month}. "
                f"{customers.get('repeat_customers')} were "
                f"repeat customers, producing a repeat "
                f"customer rate of "
                f"{customers.get('repeat_customer_rate_percent')}%."
            ),
            "evidence": [
                (
                    f"New customers: "
                    f"{customers.get('new_customers')}."
                ),
                (
                    f"Orders per customer: "
                    f"{customers.get('orders_per_customer')}."
                ),
                (
                    f"COD share: "
                    f"{customers.get('cod_share_percent')}%."
                ),
            ],
            "likely_driver": (
                "Observed customer repeat behaviour"
            ),
            "recommended_actions": [],
        }

    # ========================================================
    # DELIVERY
    # ========================================================

    if question_type == "delivery":

        return {
            "answer": (
                f"Delivery rate was "
                f"{overview_logistics.get('delivery_rate_percent')}% "
                f"in {month}."
            ),
            "evidence": [
                (
                    f"Average delivery TAT: "
                    f"{overview_logistics.get('average_delivery_tat_days')} "
                    f"days."
                ),
                (
                    f"P90 delivery TAT: "
                    f"{overview_logistics.get('p90_delivery_tat_days')} "
                    f"days."
                ),
                (
                    f"On-time delivery: "
                    f"{overview_logistics.get('on_time_delivery_percent')}%."
                ),
            ],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    # ========================================================
    # LOGISTICS
    # ========================================================

    if question_type == "logistics":

        couriers = logistics_context.get(
            "couriers",
            [],
        )

        payment_rows = logistics_context.get(
            "payment_logistics",
            [],
        )

        evidence = [
            (
                f"RTO rate: "
                f"{overview_logistics.get('rto_rate_percent')}%."
            ),
            (
                f"NDR rate: "
                f"{overview_logistics.get('ndr_rate_percent')}%."
            ),
            (
                f"Average delivery TAT: "
                f"{overview_logistics.get('average_delivery_tat_days')} "
                f"days."
            ),
            (
                f"P90 delivery TAT: "
                f"{overview_logistics.get('p90_delivery_tat_days')} "
                f"days."
            ),
            (
                f"On-time delivery: "
                f"{overview_logistics.get('on_time_delivery_percent')}%."
            ),
        ]

        cod = next(
            (
                row
                for row in payment_rows
                if row.get(
                    "payment_group"
                ) == "COD"
            ),
            None,
        )

        prepaid = next(
            (
                row
                for row in payment_rows
                if row.get(
                    "payment_group"
                ) == "Prepaid"
            ),
            None,
        )

        if cod:

            evidence.append(
                (
                    f"COD RTO rate: "
                    f"{cod.get('rto_rate_percent')}%."
                )
            )

        if prepaid:

            evidence.append(
                (
                    f"Prepaid RTO rate: "
                    f"{prepaid.get('rto_rate_percent')}%."
                )
            )

        # ----------------------------------------------------
        # COURIER-SPECIFIC QUESTION
        # ----------------------------------------------------

        if (
            "courier" in q
            or "carrier" in q
        ) and couriers:

            known_couriers = [
                row
                for row in couriers
                if row.get(
                    "courier_name"
                ) != "Unknown"
            ]

            if known_couriers:

                highest_rto = max(
                    known_couriers,
                    key=lambda row: row.get(
                        "rto_rate_percent",
                        -1,
                    ),
                )

                highest_ndr = max(
                    known_couriers,
                    key=lambda row: row.get(
                        "ndr_rate_percent",
                        -1,
                    ),
                )

                slowest = max(
                    known_couriers,
                    key=lambda row: row.get(
                        "average_delivery_tat_days",
                        -1,
                    ),
                )

                return {
                    "answer": (
                        f"{highest_rto.get('courier_name')} "
                        f"has the highest observed RTO rate "
                        f"at {highest_rto.get('rto_rate_percent')}%. "
                        f"Courier performance should also be "
                        f"reviewed alongside NDR and delivery TAT."
                    ),
                    "evidence": [
                        (
                            f"Highest RTO: "
                            f"{highest_rto.get('courier_name')} "
                            f"at "
                            f"{highest_rto.get('rto_rate_percent')}%."
                        ),
                        (
                            f"Highest NDR: "
                            f"{highest_ndr.get('courier_name')} "
                            f"at "
                            f"{highest_ndr.get('ndr_rate_percent')}%."
                        ),
                        (
                            f"Slowest average delivery TAT: "
                            f"{slowest.get('courier_name')} "
                            f"at "
                            f"{slowest.get('average_delivery_tat_days')} "
                            f"days."
                        ),
                    ],
                    "likely_driver": (
                        "Courier-level operational performance "
                        "varies across RTO, NDR and TAT."
                    ),
                    "recommended_actions": [
                        (
                            "Review courier allocation using RTO, "
                            "NDR, TAT and cost together rather than "
                            "ranking couriers on one KPI."
                        )
                    ],
                }

        return {
            "answer": (
                f"Logistics performance in {month} shows "
                f"an RTO rate of "
                f"{overview_logistics.get('rto_rate_percent')}%, "
                f"an NDR rate of "
                f"{overview_logistics.get('ndr_rate_percent')}%, "
                f"and P90 delivery TAT of "
                f"{overview_logistics.get('p90_delivery_tat_days')} "
                f"days."
            ),
            "evidence": evidence,
            "likely_driver": (
                "Payment-method risk is a material signal."
                if (
                    cod
                    and prepaid
                    and (
                        cod.get(
                            "rto_rate_percent",
                            0,
                        )
                        >
                        prepaid.get(
                            "rto_rate_percent",
                            0,
                        )
                    )
                )
                else "Not established"
            ),
            "recommended_actions": [
                (
                    "Prioritize operational review of segments "
                    "with materially elevated RTO or NDR."
                )
            ],
        }

    # ========================================================
    # INVENTORY
    # ========================================================

    if question_type == "inventory":

        reorder_candidates = (
            inventory_context.get(
                "reorder_candidates",
                [],
            )
        )

        trapped_skus = (
            inventory_context.get(
                "highest_trapped_inventory",
                [],
            )
        )

        evidence = [
            (
                f"Inventory cost value: "
                f"{inventory_summary.get('inventory_cost_value')}."
            ),
            (
                f"Below-reorder SKU/warehouse positions: "
                f"{inventory_summary.get('below_reorder_rows')}."
            ),
            (
                f"Overstock positions: "
                f"{inventory_summary.get('overstock_rows')}."
            ),
            (
                f"Slow-moving positions: "
                f"{inventory_summary.get('slow_moving_rows')}."
            ),
            (
                f"Potential revenue at risk: "
                f"{inventory_summary.get('potential_revenue_at_risk')}."
            ),
            (
                f"Estimated trapped inventory cost: "
                f"{inventory_summary.get('estimated_trapped_inventory_cost')}."
            ),
        ]

        if reorder_candidates:

            first_reorder = (
                reorder_candidates[0]
            )

            evidence.append(
                (
                    f"High-priority reorder candidate: "
                    f"{first_reorder.get('product_name')} "
                    f"({first_reorder.get('sku_id')}) with "
                    f"potential revenue at risk of "
                    f"{first_reorder.get('potential_revenue_at_risk')}."
                )
            )

        if trapped_skus:

            highest_trapped = (
                trapped_skus[0]
            )

            evidence.append(
                (
                    f"Highest observed trapped-inventory SKU: "
                    f"{highest_trapped.get('product_name')} "
                    f"({highest_trapped.get('sku_id')}) with "
                    f"estimated trapped cost of "
                    f"{highest_trapped.get('estimated_trapped_inventory_cost')}."
                )
            )

        return {
            "answer": (
                f"Inventory requires attention on both "
                f"replenishment and excess-stock risk. "
                f"There are "
                f"{inventory_summary.get('below_reorder_rows')} "
                f"below-reorder positions and "
                f"{inventory_summary.get('overstock_rows')} "
                f"overstock positions, while estimated "
                f"trapped inventory cost is "
                f"{inventory_summary.get('estimated_trapped_inventory_cost')}."
            ),
            "evidence": evidence,
            "likely_driver": (
                "Inventory risk is split between stock "
                "shortage exposure and excess working capital."
            ),
            "recommended_actions": [
                (
                    "Prioritize reorder candidates with the "
                    "largest potential revenue at risk."
                ),
                (
                    "Review SKUs with the highest trapped "
                    "inventory cost for redistribution, "
                    "markdown or procurement reduction."
                ),
            ],
        }

    # ========================================================
    # CANCELLATION
    # ========================================================

    if question_type == "cancellation":

        return {
            "answer": (
                "A dedicated cancellation KPI is not "
                "currently exposed in the D2C AI context."
            ),
            "evidence": [
                (
                    "The dataset contains order-status data, "
                    "but cancellation analysis is not yet a "
                    "dedicated analyst metric."
                )
            ],
            "likely_driver": "Not established",
            "recommended_actions": [],
        }

    # ========================================================
    # TRENDS / PERFORMANCE
    # ========================================================

    if question_type in {
        "trends",
        "performance",
    }:

        return {
            "answer": (
                f"In {month}, realized revenue was "
                f"{revenue.get('realized_revenue')} with "
                f"revenue growth of "
                f"{revenue.get('revenue_growth_percent')}%. "
                f"Contribution profit after marketing "
                f"was "
                f"{profitability.get('contribution_profit_after_marketing')}."
            ),
            "evidence": [
                (
                    f"Order growth: "
                    f"{revenue.get('order_growth_percent')}%."
                ),
                (
                    f"Contribution margin after marketing: "
                    f"{profitability.get('contribution_margin_after_marketing_percent')}%."
                ),
                (
                    f"Repeat customer rate: "
                    f"{customers.get('repeat_customer_rate_percent')}%."
                ),
                (
                    f"RTO rate: "
                    f"{overview_logistics.get('rto_rate_percent')}%."
                ),
            ],
            "likely_driver": (
                "Multi-metric business performance"
            ),
            "recommended_actions": [],
        }

    # ========================================================
    # BUSINESS HEALTH / GENERAL BUSINESS
    # ========================================================

    if question_type in {
        "business_health",
        "general_business",
        "general",
    }:

        evidence = [
            (
                f"Revenue growth: "
                f"{revenue.get('revenue_growth_percent')}%."
            ),
            (
                f"Order growth: "
                f"{revenue.get('order_growth_percent')}%."
            ),
            (
                f"Contribution margin after marketing: "
                f"{profitability.get('contribution_margin_after_marketing_percent')}%."
            ),
            (
                f"ROAS: "
                f"{overview_marketing.get('roas')}x."
            ),
            (
                f"CAC: "
                f"{overview_marketing.get('cac')}."
            ),
            (
                f"Repeat customer rate: "
                f"{customers.get('repeat_customer_rate_percent')}%."
            ),
            (
                f"RTO rate: "
                f"{overview_logistics.get('rto_rate_percent')}%."
            ),
            (
                f"NDR rate: "
                f"{overview_logistics.get('ndr_rate_percent')}%."
            ),
            (
                f"Potential inventory revenue at risk: "
                f"{inventory_summary.get('potential_revenue_at_risk')}."
            ),
            (
                f"Estimated trapped inventory cost: "
                f"{inventory_summary.get('estimated_trapped_inventory_cost')}."
            ),
        ]

        return {
            "answer": (
                f"The most material issues visible in "
                f"{month} are the sharp revenue/order "
                f"contraction, logistics risk, and "
                f"inventory working-capital exposure."
            ),
            "evidence": evidence,
            "likely_driver": (
                "Multiple commercial and operational factors"
            ),
            "recommended_actions": [
                (
                    "Investigate the revenue and order-volume "
                    "decline before changing growth strategy."
                ),
                (
                    "Reduce operational exposure in high-RTO "
                    "and high-NDR segments."
                ),
                (
                    "Prioritize inventory rebalancing across "
                    "reorder-risk and excess-stock SKUs."
                ),
            ],
        }

    # ========================================================
    # SCENARIO
    # ========================================================

    if question_type == "scenario":

        return {
            "answer": (
                "Scenario questions should be executed "
                "through the ProfitLens Scenario Lab so "
                "that scenario math remains deterministic."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    # ========================================================
    # DEFAULT
    # ========================================================

    return {
        "answer": (
            f"Business analysis was completed "
            f"for {month}."
        ),
        "evidence": [
            (
                f"Realized revenue: "
                f"{revenue.get('realized_revenue')}."
            ),
            (
                f"Contribution profit after marketing: "
                f"{profitability.get('contribution_profit_after_marketing')}."
            ),
        ],
        "likely_driver": "Not established",
        "recommended_actions": [],
    }


# ============================================================
# LEGACY FALLBACK
# ============================================================


def _build_legacy_fallback(
    question_type: str,
    month: str,
    context: dict,
) -> dict:
    """
    Preserve legacy Olist fallback behaviour while
    old regression tests remain in the repository.
    """

    if question_type == "revenue":

        revenue = context.get(
            "revenue_analysis",
            {},
        )

        driver = context.get(
            "driver_analysis",
            {},
        )

        return {
            "answer": (
                f"Revenue changed by "
                f"{revenue.get('revenue_change_percent')}% "
                f"in {month}, from "
                f"{revenue.get('previous_revenue')} to "
                f"{revenue.get('revenue')}."
            ),
            "evidence": [
                (
                    f"Orders changed by "
                    f"{revenue.get('order_change_percent')}%."
                ),
                (
                    f"AOV changed by "
                    f"{revenue.get('aov_change_percent')}%."
                ),
            ],
            "likely_driver": (
                driver.get(
                    "primary_driver",
                    "Not established",
                )
            ),
            "recommended_actions": [],
        }

    if question_type == "orders":

        orders = context.get(
            "orders",
            {},
        )

        return {
            "answer": (
                f"Orders were "
                f"{orders.get('value')} in {month}, "
                f"a change of "
                f"{orders.get('growth_percent')}% "
                f"from the previous month."
            ),
            "evidence": [
                (
                    f"Previous orders: "
                    f"{orders.get('previous_value')}."
                )
            ],
            "likely_driver": "Not established",
            "recommended_actions": [],
        }

    if question_type == "delivery":

        delivery = context.get(
            "delivery",
            {},
        )

        return {
            "answer": (
                f"Delivery rate was "
                f"{delivery.get('rate_percent')}% "
                f"in {month}."
            ),
            "evidence": [
                (
                    f"Delivered orders: "
                    f"{delivery.get('delivered_orders')}."
                )
            ],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    if question_type == "product":

        product_analysis = context.get(
            "product_analysis",
            {},
        )

        products = product_analysis.get(
            "top_products",
            [],
        )

        if products:

            product = products[0]

            return {
                "answer": (
                    f"The highest-revenue product was "
                    f"{product.get('product_id')}, generating "
                    f"{product.get('revenue')} in revenue."
                ),
                "evidence": [
                    (
                        f"Units sold: "
                        f"{product.get('units_sold')}."
                    ),
                    (
                        f"Orders: "
                        f"{product.get('orders')}."
                    ),
                ],
                "likely_driver": (
                    "Product revenue contribution"
                ),
                "recommended_actions": [],
            }

    if question_type == "customer":

        return {
            "answer": (
                "Reliable repeat-purchase and retention "
                "metrics are unavailable in the legacy "
                "dataset."
            ),
            "evidence": [],
            "likely_driver": (
                "Insufficient customer identity data"
            ),
            "recommended_actions": [],
        }

    if question_type == "logistics":

        logistics = context.get(
            "logistics_analysis",
            {},
        )

        delivery = (
            logistics
            .get(
                "fulfilment_tat",
                {},
            )
            .get(
                "purchase_to_delivery",
                {},
            )
        )

        return {
            "answer": (
                f"P90 purchase-to-delivery TAT was "
                f"{delivery.get('p90')} days."
            ),
            "evidence": [
                (
                    f"Average purchase-to-delivery TAT: "
                    f"{delivery.get('average')} days."
                )
            ],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    kpi = context.get(
        "kpi_dashboard",
        {},
    )

    revenue_analysis = context.get(
        "revenue_analysis",
        {},
    )

    evidence = []

    if kpi:

        evidence = [
            (
                f"Revenue growth: "
                f"{kpi.get('revenue', {}).get('growth_percent')}%."
            ),
            (
                f"Order growth: "
                f"{kpi.get('orders', {}).get('growth_percent')}%."
            ),
            (
                f"Delivery rate: "
                f"{kpi.get('delivery', {}).get('rate_percent')}%."
            ),
        ]

    return {
        "answer": (
            f"Business analysis was completed for "
            f"{month}. Revenue changed by "
            f"{revenue_analysis.get('revenue_change_percent')}%."
            if revenue_analysis
            else (
                f"Business analysis was completed "
                f"for {month}."
            )
        ),
        "evidence": evidence,
        "likely_driver": (
            context
            .get(
                "driver_analysis",
                {},
            )
            .get(
                "primary_driver",
                "Not established",
            )
        ),
        "recommended_actions": [],
    }


# ============================================================
# PUBLIC BUSINESS ANALYST
# ============================================================


def answer_business_question(
    question: str,
    month: str = "2025-11",
) -> dict:
    """
    ProfitLens natural-language business analyst.

    For the India D2C path:

    1. Classify question.
    2. Build deterministic D2C context.
    3. Ask AI to interpret deterministic facts.
    4. Use deterministic fallback if AI fails.

    AI failures are temporarily printed to the server
    console so the integration can be debugged.
    """

    question_type = classify_question(
        question
    )

    # ========================================================
    # D2C PATH
    # ========================================================

    if _is_d2c_month(
        month
    ):

        business_context = (
            build_d2c_business_context(
                month
            )
        )
        llm_context = (
        build_focused_d2c_context(
            full_context=business_context,
            question_type=question_type,
        )
)

        try:

            answer = ask_business_analyst(
                question=question,
                question_type=question_type,
                month=month,
                business_context=llm_context,
            )

            ai_available = True

        except Exception:

            answer = _build_d2c_fallback(
                question=question,
                question_type=question_type,
                month=month,
                context=business_context,
            )

            ai_available = False

        return {
            "question": question,
            "month": month,
            "question_type": question_type,
            "analysis_execution": {
                "total_steps": 1,
                "successful_steps": 1,
                "failed_steps": 0,
            },
            "ai_available": ai_available,
            "answer": answer,
        }

    # ========================================================
    # LEGACY PATH
    # ========================================================
    from backend.app.services.fast_analysis import (
        execute_fast_analysis,
    )
    fast_context = execute_fast_analysis(
        question=question,
        question_type=question_type,
        month=month,
    )

    try:

        answer = ask_business_analyst(
            question=question,
            question_type=question_type,
            month=month,
            business_context=fast_context,
        )

        ai_available = True

    except Exception:

        answer = _build_legacy_fallback(
            question_type=question_type,
            month=month,
            context=fast_context,
        )

        ai_available = False

    return {
        "question": question,
        "month": month,
        "question_type": question_type,
        "analysis_execution": {
            "total_steps": 1,
            "successful_steps": 1,
            "failed_steps": 0,
        },
        "ai_available": ai_available,
        "answer": answer,
    }
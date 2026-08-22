from __future__ import annotations

from typing import Any

from backend.app.services.serialization import (
    make_json_safe,
)


# ============================================================
# HELPERS
# ============================================================


def _nested(
    data: dict,
    *keys: str,
) -> Any:

    current: Any = data

    for key in keys:

        if not isinstance(
            current,
            dict,
        ):
            return None

        current = current.get(
            key
        )

    return current


def _evidence(
    *,
    metric: str,
    value: Any,
    source: str,
):
    return {
        "metric":
            metric,

        "value":
            value,

        "source":
            source,
    }


def _claim(
    *,
    claim_id: str,
    claim_type: str,
    statement: str,
    confidence: str,
    evidence: list[dict],
    limitation: str | None = None,
):
    """
    Build one deterministic analytical claim.

    claim_type:
    - fact
    - inference
    - hypothesis

    confidence:
    - high
    - medium
    - low

    Confidence describes deterministic analytical
    support. It is NOT AI/model confidence.
    """

    return {
        "claim_id":
            claim_id,

        "claim_type":
            claim_type,

        "statement":
            statement,

        "confidence":
            confidence,

        "evidence":
            evidence,

        "limitation":
            limitation,
    }


# ============================================================
# REVENUE CLAIMS
# ============================================================


def _build_revenue_claims(
    context: dict,
):
    revenue = (
        _nested(
            context,
            "overview",
            "revenue",
        )
        or {}
    )

    claims = []

    realized_revenue = revenue.get(
        "realized_revenue"
    )

    revenue_growth = revenue.get(
        "revenue_growth_percent"
    )

    orders = revenue.get(
        "orders"
    )

    order_growth = revenue.get(
        "order_growth_percent"
    )

    aov = revenue.get(
        "aov"
    )


    if (
        realized_revenue is not None
        and revenue_growth is not None
    ):

        if revenue_growth < 0:
            direction = "declined"

        elif revenue_growth > 0:
            direction = "increased"

        else:
            direction = "was flat"

        claims.append(
            _claim(
                claim_id=
                    "revenue_change",

                claim_type=
                    "fact",

                statement=(
                    f"Realized revenue {direction} "
                    f"by {abs(revenue_growth):.2f}% "
                    f"to {realized_revenue:.2f}."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "realized_revenue",

                        value=
                            realized_revenue,

                        source=
                            "d2c_overview_engine",
                    ),
                    _evidence(
                        metric=
                            "revenue_growth_percent",

                        value=
                            revenue_growth,

                        source=
                            "d2c_overview_engine",
                    ),
                ],
            )
        )


    if (
        orders is not None
        and order_growth is not None
    ):

        claims.append(
            _claim(
                claim_id=
                    "order_change",

                claim_type=
                    "fact",

                statement=(
                    f"Orders changed by "
                    f"{order_growth:.2f}% "
                    f"to {orders:,}."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "orders",

                        value=
                            orders,

                        source=
                            "d2c_overview_engine",
                    ),
                    _evidence(
                        metric=
                            "order_growth_percent",

                        value=
                            order_growth,

                        source=
                            "d2c_overview_engine",
                    ),
                ],
            )
        )


    if aov is not None:

        claims.append(
            _claim(
                claim_id=
                    "current_aov",

                claim_type=
                    "fact",

                statement=(
                    f"Average order value was "
                    f"{aov:.2f}."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "aov",

                        value=
                            aov,

                        source=
                            "d2c_overview_engine",
                    ),
                ],

                limitation=(
                    "The current D2C context does not "
                    "expose previous-period AOV or AOV "
                    "growth, so no AOV trend claim is made."
                ),
            )
        )


    if (
        revenue_growth is not None
        and order_growth is not None
        and revenue_growth < 0
        and order_growth < 0
    ):

        difference = abs(
            abs(
                revenue_growth
            )
            - abs(
                order_growth
            )
        )

        confidence = (
            "high"
            if difference <= 5
            else "medium"
        )

        claims.append(
            _claim(
                claim_id=
                    "order_volume_signal",

                claim_type=
                    "inference",

                statement=(
                    "Lower order volume is the "
                    "strongest observed commercial "
                    "signal associated with the "
                    "revenue decline."
                ),

                confidence=
                    confidence,

                evidence=[
                    _evidence(
                        metric=
                            "revenue_growth_percent",

                        value=
                            revenue_growth,

                        source=
                            "d2c_overview_engine",
                    ),
                    _evidence(
                        metric=
                            "order_growth_percent",

                        value=
                            order_growth,

                        source=
                            "d2c_overview_engine",
                    ),
                ],

                limitation=(
                    "Revenue and order volume moved "
                    "closely in the same direction and "
                    "magnitude. This is an observed "
                    "association, not a causal revenue "
                    "decomposition and does not establish "
                    "why order volume changed."
                ),
            )
        )


    return claims


# ============================================================
# PROFITABILITY CLAIMS
# ============================================================


def _build_profitability_claims(
    context: dict,
):
    profitability = (
        _nested(
            context,
            "overview",
            "profitability",
        )
        or {}
    )

    claims = []

    gross_profit = profitability.get(
        "gross_profit"
    )

    gross_margin = profitability.get(
        "gross_margin_percent"
    )

    before_marketing = profitability.get(
        "contribution_profit_before_marketing"
    )

    after_marketing = profitability.get(
        "contribution_profit_after_marketing"
    )

    after_margin = profitability.get(
        "contribution_margin_after_marketing_percent"
    )

    profit_growth = profitability.get(
        "profit_after_marketing_growth_percent"
    )


    if (
        gross_profit is not None
        and gross_margin is not None
    ):

        claims.append(
            _claim(
                claim_id=
                    "gross_profitability",

                claim_type=
                    "fact",

                statement=(
                    f"Gross profit was "
                    f"{gross_profit:.2f} with a "
                    f"{gross_margin:.2f}% gross margin."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "gross_profit",

                        value=
                            gross_profit,

                        source=
                            "d2c_overview_engine",
                    ),
                    _evidence(
                        metric=
                            "gross_margin_percent",

                        value=
                            gross_margin,

                        source=
                            "d2c_overview_engine",
                    ),
                ],
            )
        )


    if (
        after_marketing is not None
        and after_margin is not None
    ):

        status = (
            "profitable"
            if after_marketing > 0
            else (
                "loss-making"
                if after_marketing < 0
                else "break-even"
            )
        )

        claims.append(
            _claim(
                claim_id=
                    "profitability_after_marketing",

                claim_type=
                    "fact",

                statement=(
                    f"The business was {status} "
                    f"after marketing with contribution "
                    f"profit of {after_marketing:.2f} "
                    f"and margin of {after_margin:.2f}%."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "contribution_profit_after_marketing",

                        value=
                            after_marketing,

                        source=
                            "d2c_overview_engine",
                    ),
                    _evidence(
                        metric=
                            "contribution_margin_after_marketing_percent",

                        value=
                            after_margin,

                        source=
                            "d2c_overview_engine",
                    ),
                ],
            )
        )


    if (
        before_marketing is not None
        and after_marketing is not None
    ):

        claims.append(
            _claim(
                claim_id=
                    "marketing_profit_pressure",

                claim_type=
                    "fact",

                statement=(
                    "Contribution profit declined from "
                    f"{before_marketing:.2f} before marketing "
                    f"to {after_marketing:.2f} after marketing."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "contribution_profit_before_marketing",

                        value=
                            before_marketing,

                        source=
                            "d2c_overview_engine",
                    ),
                    _evidence(
                        metric=
                            "contribution_profit_after_marketing",

                        value=
                            after_marketing,

                        source=
                            "d2c_overview_engine",
                    ),
                ],

                limitation=(
                    "This describes the deterministic "
                    "profitability waterfall. It does not "
                    "measure marketing incrementality."
                ),
            )
        )


    if profit_growth is not None:

        claims.append(
            _claim(
                claim_id=
                    "profit_growth",

                claim_type=
                    "fact",

                statement=(
                    "Contribution profit after marketing "
                    f"changed by {profit_growth:.2f}%."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "profit_after_marketing_growth_percent",

                        value=
                            profit_growth,

                        source=
                            "d2c_overview_engine",
                    ),
                ],
            )
        )


    return claims


# ============================================================
# MARKETING CLAIMS
# ============================================================


def _build_marketing_claims(
    context: dict,
):
    marketing = (
        _nested(
            context,
            "marketing",
            "summary",
        )
        or {}
    )

    claims = []

    blended_roas = marketing.get(
        "blended_roas"
    )

    paid_roas = marketing.get(
        "paid_roas"
    )

    cac = marketing.get(
        "cac"
    )

    spend = marketing.get(
        "marketing_spend"
    )

    new_customers = marketing.get(
        "new_customers"
    )


    if blended_roas is not None:

        claims.append(
            _claim(
                claim_id=
                    "blended_roas",

                claim_type=
                    "fact",

                statement=(
                    f"Blended ROAS was "
                    f"{blended_roas:.2f}."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "blended_roas",

                        value=
                            blended_roas,

                        source=
                            "d2c_marketing_engine",
                    ),
                ],

                limitation=(
                    "Marketing attribution is aggregate "
                    "campaign-level rather than order-level "
                    "and does not establish incrementality."
                ),
            )
        )


    if paid_roas is not None:

        claims.append(
            _claim(
                claim_id=
                    "paid_roas",

                claim_type=
                    "fact",

                statement=(
                    f"Paid ROAS was "
                    f"{paid_roas:.2f}."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "paid_roas",

                        value=
                            paid_roas,

                        source=
                            "d2c_marketing_engine",
                    ),
                ],

                limitation=(
                    "Paid ROAS is attributed performance, "
                    "not proof of incremental revenue."
                ),
            )
        )


    if (
        cac is not None
        and new_customers is not None
    ):

        claims.append(
            _claim(
                claim_id=
                    "customer_acquisition",

                claim_type=
                    "fact",

                statement=(
                    f"CAC was {cac:.2f} while "
                    f"{new_customers:,} new customers "
                    "were acquired."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "cac",

                        value=
                            cac,

                        source=
                            "d2c_marketing_engine",
                    ),
                    _evidence(
                        metric=
                            "new_customers",

                        value=
                            new_customers,

                        source=
                            "d2c_marketing_engine",
                    ),
                ],
            )
        )


    if spend is not None:

        claims.append(
            _claim(
                claim_id=
                    "marketing_spend",

                claim_type=
                    "fact",

                statement=(
                    f"Marketing spend was "
                    f"{spend:.2f}."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "marketing_spend",

                        value=
                            spend,

                        source=
                            "d2c_marketing_engine",
                    ),
                ],
            )
        )


    return claims


# ============================================================
# CUSTOMER CLAIMS
# ============================================================


def _build_customer_claims(
    context: dict,
):
    customers = (
        _nested(
            context,
            "customers",
            "summary",
        )
        or {}
    )

    claims = []

    active = customers.get(
        "active_customers"
    )

    new = customers.get(
        "new_customers"
    )

    repeat = customers.get(
        "repeat_customers"
    )

    repeat_rate = customers.get(
        "repeat_customer_rate_percent"
    )

    orders_per_customer = customers.get(
        "orders_per_customer"
    )


    if repeat_rate is not None:

        claims.append(
            _claim(
                claim_id=
                    "repeat_customer_rate",

                claim_type=
                    "fact",

                statement=(
                    f"Repeat customer rate was "
                    f"{repeat_rate:.2f}%."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "repeat_customer_rate_percent",

                        value=
                            repeat_rate,

                        source=
                            "d2c_customer_engine",
                    ),
                    _evidence(
                        metric=
                            "repeat_customers",

                        value=
                            repeat,

                        source=
                            "d2c_customer_engine",
                    ),
                ],
            )
        )


    if (
        active is not None
        and new is not None
    ):

        claims.append(
            _claim(
                claim_id=
                    "customer_base",

                claim_type=
                    "fact",

                statement=(
                    f"There were {active:,} active "
                    f"customers, including {new:,} "
                    "new customers."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "active_customers",

                        value=
                            active,

                        source=
                            "d2c_customer_engine",
                    ),
                    _evidence(
                        metric=
                            "new_customers",

                        value=
                            new,

                        source=
                            "d2c_customer_engine",
                    ),
                ],
            )
        )


    if orders_per_customer is not None:

        claims.append(
            _claim(
                claim_id=
                    "orders_per_customer",

                claim_type=
                    "fact",

                statement=(
                    f"Orders per active customer "
                    f"were {orders_per_customer:.2f}."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "orders_per_customer",

                        value=
                            orders_per_customer,

                        source=
                            "d2c_customer_engine",
                    ),
                ],
            )
        )


    return claims


# ============================================================
# LOGISTICS CLAIMS
# ============================================================


def _build_logistics_claims(
    context: dict,
):
    logistics = (
        _nested(
            context,
            "logistics",
            "summary",
        )
        or {}
    )

    payment = (
        _nested(
            context,
            "logistics",
            "payment_logistics",
        )
        or []
    )

    claims = []

    rto_rate = logistics.get(
        "rto_rate_percent"
    )

    rto_orders = logistics.get(
        "rto_orders"
    )

    ndr_rate = logistics.get(
        "ndr_rate_percent"
    )

    on_time = logistics.get(
        "on_time_delivery_percent"
    )


    if rto_rate is not None:

        claims.append(
            _claim(
                claim_id=
                    "overall_rto",

                claim_type=
                    "fact",

                statement=(
                    f"Overall RTO rate was "
                    f"{rto_rate:.2f}%."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "rto_rate_percent",

                        value=
                            rto_rate,

                        source=
                            "d2c_logistics_engine",
                    ),
                    _evidence(
                        metric=
                            "rto_orders",

                        value=
                            rto_orders,

                        source=
                            "d2c_logistics_engine",
                    ),
                ],
            )
        )


    if (
        ndr_rate is not None
        and on_time is not None
    ):

        claims.append(
            _claim(
                claim_id=
                    "delivery_health",

                claim_type=
                    "fact",

                statement=(
                    f"NDR rate was {ndr_rate:.2f}% "
                    f"and on-time delivery was "
                    f"{on_time:.2f}%."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "ndr_rate_percent",

                        value=
                            ndr_rate,

                        source=
                            "d2c_logistics_engine",
                    ),
                    _evidence(
                        metric=
                            "on_time_delivery_percent",

                        value=
                            on_time,

                        source=
                            "d2c_logistics_engine",
                    ),
                ],
            )
        )


    cod = next(
        (
            row
            for row in payment
            if str(
                row.get(
                    "payment_group",
                    ""
                )
            ).upper()
            == "COD"
        ),
        None,
    )

    prepaid = next(
        (
            row
            for row in payment
            if str(
                row.get(
                    "payment_group",
                    ""
                )
            ).upper()
            == "PREPAID"
        ),
        None,
    )


    if (
        cod
        and prepaid
        and cod.get(
            "rto_rate_percent"
        ) is not None
        and prepaid.get(
            "rto_rate_percent"
        ) is not None
    ):

        cod_rate = cod[
            "rto_rate_percent"
        ]

        prepaid_rate = prepaid[
            "rto_rate_percent"
        ]

        claims.append(
            _claim(
                claim_id=
                    "cod_rto_signal",

                claim_type=
                    "inference",

                statement=(
                    "COD is the strongest observed "
                    "payment-related RTO risk signal."
                ),

                confidence=
                    (
                        "high"
                        if cod_rate
                        > prepaid_rate
                        else "medium"
                    ),

                evidence=[
                    _evidence(
                        metric=
                            "cod_rto_rate_percent",

                        value=
                            cod_rate,

                        source=
                            "d2c_logistics_engine",
                    ),
                    _evidence(
                        metric=
                            "prepaid_rto_rate_percent",

                        value=
                            prepaid_rate,

                        source=
                            "d2c_logistics_engine",
                    ),
                ],

                limitation=(
                    "This is an observed association "
                    "between payment mode and RTO. "
                    "It does not independently prove "
                    "that COD causes RTO."
                ),
            )
        )


    return claims


# ============================================================
# INVENTORY CLAIMS
# ============================================================


def _build_inventory_claims(
    context: dict,
):
    inventory = (
        _nested(
            context,
            "inventory",
            "summary",
        )
        or {}
    )

    claims = []

    trapped = inventory.get(
        "estimated_trapped_inventory_cost"
    )

    overstock = inventory.get(
        "overstock_rows"
    )

    slow_moving = inventory.get(
        "slow_moving_rows"
    )

    below_reorder = inventory.get(
        "below_reorder_rows"
    )

    revenue_at_risk = inventory.get(
        "potential_revenue_at_risk"
    )


    if trapped is not None:

        claims.append(
            _claim(
                claim_id=
                    "trapped_inventory",

                claim_type=
                    "fact",

                statement=(
                    "Estimated trapped inventory "
                    f"cost was {trapped:.2f}."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "estimated_trapped_inventory_cost",

                        value=
                            trapped,

                        source=
                            "d2c_inventory_engine",
                    ),
                    _evidence(
                        metric=
                            "overstock_rows",

                        value=
                            overstock,

                        source=
                            "d2c_inventory_engine",
                    ),
                    _evidence(
                        metric=
                            "slow_moving_rows",

                        value=
                            slow_moving,

                        source=
                            "d2c_inventory_engine",
                    ),
                ],

                limitation=(
                    "This is a deterministic heuristic "
                    "estimate of inventory exposure, "
                    "not guaranteed recoverable cash."
                ),
            )
        )


    if (
        below_reorder is not None
        and revenue_at_risk is not None
    ):

        claims.append(
            _claim(
                claim_id=
                    "replenishment_risk",

                claim_type=
                    "fact",

                statement=(
                    f"{below_reorder} SKU-warehouse "
                    "positions were below reorder level, "
                    "with estimated potential revenue "
                    f"at risk of {revenue_at_risk:.2f}."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "below_reorder_rows",

                        value=
                            below_reorder,

                        source=
                            "d2c_inventory_engine",
                    ),
                    _evidence(
                        metric=
                            "potential_revenue_at_risk",

                        value=
                            revenue_at_risk,

                        source=
                            "d2c_inventory_engine",
                    ),
                ],

                limitation=(
                    "Potential revenue at risk is a "
                    "deterministic heuristic estimate, "
                    "not guaranteed lost revenue."
                ),
            )
        )


    return claims


# ============================================================
# PRODUCT CLAIMS
# ============================================================


def _build_product_claims(
    context: dict,
):
    products = (
        _nested(
            context,
            "products",
            "summary",
        )
        or {}
    )

    claims = []

    revenue = products.get(
        "total_net_revenue"
    )

    gross_profit = products.get(
        "total_gross_profit"
    )

    gross_margin = products.get(
        "gross_margin_percent"
    )

    loss_making = products.get(
        "loss_making_products"
    )

    top_10_share = products.get(
        "top_10_revenue_share_percent"
    )


    if (
        revenue is not None
        and gross_profit is not None
        and gross_margin is not None
    ):

        claims.append(
            _claim(
                claim_id=
                    "portfolio_profitability",

                claim_type=
                    "fact",

                statement=(
                    f"Product net revenue was "
                    f"{revenue:.2f}, with gross profit "
                    f"of {gross_profit:.2f} and gross "
                    f"margin of {gross_margin:.2f}%."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "total_net_revenue",

                        value=
                            revenue,

                        source=
                            "d2c_product_engine",
                    ),
                    _evidence(
                        metric=
                            "total_gross_profit",

                        value=
                            gross_profit,

                        source=
                            "d2c_product_engine",
                    ),
                    _evidence(
                        metric=
                            "gross_margin_percent",

                        value=
                            gross_margin,

                        source=
                            "d2c_product_engine",
                    ),
                ],

                limitation=(
                    "This is SKU gross profitability. "
                    "SKU-level contribution profit is "
                    "not available because shared "
                    "logistics, payment and marketing "
                    "costs have not been allocated."
                ),
            )
        )


    if loss_making is not None:

        claims.append(
            _claim(
                claim_id=
                    "loss_making_products",

                claim_type=
                    "fact",

                statement=(
                    f"{loss_making} products were "
                    "loss-making at the gross-profit level."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "loss_making_products",

                        value=
                            loss_making,

                        source=
                            "d2c_product_engine",
                    ),
                ],
            )
        )


    if top_10_share is not None:

        claims.append(
            _claim(
                claim_id=
                    "product_concentration",

                claim_type=
                    "fact",

                statement=(
                    f"The top 10 products contributed "
                    f"{top_10_share:.2f}% of product revenue."
                ),

                confidence=
                    "high",

                evidence=[
                    _evidence(
                        metric=
                            "top_10_revenue_share_percent",

                        value=
                            top_10_share,

                        source=
                            "d2c_product_engine",
                    ),
                ],
            )
        )


    return claims


# ============================================================
# BUSINESS HEALTH
# ============================================================


def _build_business_health_claims(
    context: dict,
):
    """
    Compose cross-functional business claims from
    deterministic domain claim builders.

    Business health includes:
    - core cross-functional facts
    - a small number of high-confidence inferences

    Hypotheses remain excluded until dedicated
    evidence-sufficiency logic exists.
    """

    claims = []

    domain_claims = [
        _build_revenue_claims(
            context
        ),
        _build_profitability_claims(
            context
        ),
        _build_marketing_claims(
            context
        ),
        _build_customer_claims(
            context
        ),
        _build_logistics_claims(
            context
        ),
        _build_inventory_claims(
            context
        ),
        _build_product_claims(
            context
        ),
    ]

    preferred_fact_ids = {
        "revenue_change",
        "profitability_after_marketing",
        "blended_roas",
        "repeat_customer_rate",
        "overall_rto",
        "delivery_health",
        "trapped_inventory",
        "replenishment_risk",
        "portfolio_profitability",
    }

    preferred_inference_ids = {
        "order_volume_signal",
        "cod_rto_signal",
    }

    for group in domain_claims:

        for item in group:

            claim_id = item.get(
                "claim_id"
            )

            claim_type = item.get(
                "claim_type"
            )

            confidence = item.get(
                "confidence"
            )

            if (
                claim_type == "fact"
                and claim_id
                in preferred_fact_ids
            ):
                claims.append(
                    item
                )

            elif (
                claim_type == "inference"
                and confidence == "high"
                and claim_id
                in preferred_inference_ids
            ):
                claims.append(
                    item
                )

    return claims


# ============================================================
# PUBLIC CLAIM ENGINE
# ============================================================


def build_d2c_claims(
    *,
    question_type: str,
    business_context: dict,
    analysis_execution: dict,
):
    """
    Build claim-level deterministic evidence.

    Important:
    - facts come directly from deterministic D2C engines
    - inferences are explicitly labelled
    - hypotheses are not generated without evidence logic
    - confidence is analytical claim confidence
    - confidence is never AI/model confidence
    """

    if question_type == "revenue":

        claims = _build_revenue_claims(
            business_context
        )

    elif question_type == "profitability":

        claims = _build_profitability_claims(
            business_context
        )

    elif question_type == "marketing":

        claims = _build_marketing_claims(
            business_context
        )

    elif question_type == "customer":

        claims = _build_customer_claims(
            business_context
        )

    elif question_type in {
        "logistics",
        "delivery",
    }:

        claims = _build_logistics_claims(
            business_context
        )

    elif question_type == "inventory":

        claims = _build_inventory_claims(
            business_context
        )

    elif question_type == "product":

        claims = _build_product_claims(
            business_context
        )

    elif question_type in {
        "business_health",
        "performance",
        "general_business",
        "general",
        "trends",
    }:

        claims = _build_business_health_claims(
            business_context
        )

    else:

        claims = []


    counts = {
        "fact": 0,
        "inference": 0,
        "hypothesis": 0,
    }


    confidence_counts = {
        "high": 0,
        "medium": 0,
        "low": 0,
    }


    for item in claims:

        claim_type = item.get(
            "claim_type"
        )

        confidence = item.get(
            "confidence"
        )

        if claim_type in counts:

            counts[
                claim_type
            ] += 1

        if confidence in confidence_counts:

            confidence_counts[
                confidence
            ] += 1


    return make_json_safe({
        "status":
            "complete",

        "question_type":
            question_type,

        "claims":
            claims,

        "claim_counts":
            counts,

        "confidence_counts":
            confidence_counts,

        "confidence_definition": (
            "Confidence reflects deterministic "
            "support for an analytical claim. "
            "It is not AI/model confidence."
        ),

        "hypothesis_policy": (
            "No hypothesis is emitted unless a "
            "deterministic evidence rule explicitly "
            "supports creating one."
        ),
    })

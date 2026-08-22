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


def _missing(
    *,
    evidence_id: str,
    description: str,
    reason: str,
    suggested_source: str | None = None,
):
    return {
        "evidence_id":
            evidence_id,

        "description":
            description,

        "reason":
            reason,

        "suggested_source":
            suggested_source,
    }


def _hypothesis(
    *,
    hypothesis_id: str,
    domain: str,
    statement: str,
    related_claim: str | None,
    current_evidence: list[dict],
    missing_evidence: list[dict],
    test: str,
):
    """
    Create one evidence-aware hypothesis.

    Hypotheses are deliberately NOT treated as facts.

    Status rules:
    - untested:
        no meaningful current supporting observation
    - insufficient_evidence:
        current observations exist but required causal
        evidence is missing
    - supported:
        reserved for future use when deterministic
        hypothesis tests are implemented
    """

    if current_evidence:

        status = (
            "insufficient_evidence"
            if missing_evidence
            else "supported"
        )

    else:

        status = "untested"


    if status == "supported":

        confidence = "high"

    elif current_evidence:

        confidence = "low"

    else:

        confidence = "low"


    return {
        "hypothesis_id":
            hypothesis_id,

        "domain":
            domain,

        "statement":
            statement,

        "related_claim":
            related_claim,

        "status":
            status,

        "confidence":
            confidence,

        "current_evidence":
            current_evidence,

        "missing_evidence":
            missing_evidence,

        "test":
            test,

        "guardrail": (
            "This is a hypothesis, not an "
            "established causal conclusion."
        ),
    }


# ============================================================
# REVENUE HYPOTHESES
# ============================================================


def _build_revenue_hypotheses(
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

    marketing = (
        _nested(
            context,
            "marketing",
            "summary",
        )
        or {}
    )

    customers = (
        _nested(
            context,
            "customers",
            "summary",
        )
        or {}
    )

    inventory = (
        _nested(
            context,
            "inventory",
            "summary",
        )
        or {}
    )


    revenue_growth = revenue.get(
        "revenue_growth_percent"
    )

    order_growth = revenue.get(
        "order_growth_percent"
    )

    active_customers = customers.get(
        "active_customers"
    )

    new_customers = customers.get(
        "new_customers"
    )

    sessions = marketing.get(
        "sessions"
    )

    session_conversion = marketing.get(
        "session_conversion_percent"
    )

    below_reorder = inventory.get(
        "below_reorder_rows"
    )


    hypotheses = []


    # --------------------------------------------------------
    # DEMAND / TRAFFIC
    # --------------------------------------------------------

    current_evidence = []

    if (
        revenue_growth is not None
        and revenue_growth < 0
    ):

        current_evidence.append(
            _evidence(
                metric=
                    "revenue_growth_percent",

                value=
                    revenue_growth,

                source=
                    "d2c_overview_engine",
            )
        )

    if (
        order_growth is not None
        and order_growth < 0
    ):

        current_evidence.append(
            _evidence(
                metric=
                    "order_growth_percent",

                value=
                    order_growth,

                source=
                    "d2c_overview_engine",
            )
        )


    hypotheses.append(
        _hypothesis(
            hypothesis_id=
                "revenue_demand_weakness",

            domain=
                "revenue",

            statement=(
                "Lower customer demand or lower "
                "qualified traffic may have contributed "
                "to the decline in order volume."
            ),

            related_claim=
                "order_volume_signal",

            current_evidence=
                current_evidence,

            missing_evidence=[
                _missing(
                    evidence_id=
                        "traffic_trend",

                    description=(
                        "Previous-period sessions or "
                        "qualified traffic."
                    ),

                    reason=(
                        "Current sessions alone cannot "
                        "establish whether traffic declined."
                    ),

                    suggested_source=
                        "marketing_traffic_history",
                ),

                _missing(
                    evidence_id=
                        "conversion_trend",

                    description=(
                        "Previous-period session "
                        "conversion rate."
                    ),

                    reason=(
                        "Conversion deterioration cannot "
                        "be separated from traffic decline "
                        "without historical conversion."
                    ),

                    suggested_source=
                        "marketing_conversion_history",
                ),
            ],

            test=(
                "Compare traffic and conversion with the "
                "previous reporting period and quantify "
                "their contributions to the order decline."
            ),
        )
    )


    # --------------------------------------------------------
    # CUSTOMER ACQUISITION
    # --------------------------------------------------------

    acquisition_evidence = []

    if new_customers is not None:

        acquisition_evidence.append(
            _evidence(
                metric=
                    "new_customers",

                value=
                    new_customers,

                source=
                    "d2c_customer_engine",
            )
        )

    if active_customers is not None:

        acquisition_evidence.append(
            _evidence(
                metric=
                    "active_customers",

                value=
                    active_customers,

                source=
                    "d2c_customer_engine",
            )
        )


    hypotheses.append(
        _hypothesis(
            hypothesis_id=
                "revenue_acquisition_weakness",

            domain=
                "customer",

            statement=(
                "Weaker customer acquisition may have "
                "contributed to lower order volume."
            ),

            related_claim=
                "order_volume_signal",

            current_evidence=
                acquisition_evidence,

            missing_evidence=[
                _missing(
                    evidence_id=
                        "new_customer_trend",

                    description=(
                        "Previous-period new-customer "
                        "count and acquisition growth."
                    ),

                    reason=(
                        "The current new-customer count "
                        "does not show whether acquisition "
                        "weakened."
                    ),

                    suggested_source=
                        "customer_history",
                ),

                _missing(
                    evidence_id=
                        "channel_acquisition_trend",

                    description=(
                        "Historical new customers and CAC "
                        "by acquisition channel."
                    ),

                    reason=(
                        "Needed to identify whether a "
                        "specific acquisition source drove "
                        "the decline."
                    ),

                    suggested_source=
                        "marketing_channel_history",
                ),
            ],

            test=(
                "Compare new-customer volume and CAC by "
                "channel with the previous reporting period."
            ),
        )
    )


    # --------------------------------------------------------
    # PRODUCT AVAILABILITY
    # --------------------------------------------------------

    inventory_evidence = []

    if (
        below_reorder is not None
        and below_reorder > 0
    ):

        inventory_evidence.append(
            _evidence(
                metric=
                    "below_reorder_rows",

                value=
                    below_reorder,

                source=
                    "d2c_inventory_engine",
            )
        )


    hypotheses.append(
        _hypothesis(
            hypothesis_id=
                "revenue_inventory_constraint",

            domain=
                "inventory",

            statement=(
                "Product availability constraints may "
                "have reduced order capture."
            ),

            related_claim=
                "order_volume_signal",

            current_evidence=
                inventory_evidence,

            missing_evidence=[
                _missing(
                    evidence_id=
                        "historical_stockouts",

                    description=(
                        "Historical stockout and "
                        "below-reorder data by SKU."
                    ),

                    reason=(
                        "Inventory is currently a snapshot, "
                        "so current stock risk cannot prove "
                        "that availability constrained "
                        "November demand."
                    ),

                    suggested_source=
                        "inventory_history",
                ),

                _missing(
                    evidence_id=
                        "lost_demand_by_sku",

                    description=(
                        "Traffic or attempted demand for "
                        "unavailable SKUs."
                    ),

                    reason=(
                        "Required to connect stock "
                        "availability to lost orders."
                    ),

                    suggested_source=
                        "product_availability_events",
                ),
            ],

            test=(
                "Join SKU availability history with product "
                "traffic and orders to estimate whether "
                "stock constraints reduced order capture."
            ),
        )
    )


    return hypotheses


# ============================================================
# LOGISTICS / RTO HYPOTHESES
# ============================================================


def _build_logistics_hypotheses(
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

    zones = (
        _nested(
            context,
            "logistics",
            "zones",
        )
        or []
    )

    couriers = (
        _nested(
            context,
            "logistics",
            "couriers",
        )
        or []
    )


    rto_rate = logistics.get(
        "rto_rate_percent"
    )

    ndr_rate = logistics.get(
        "ndr_rate_percent"
    )


    hypotheses = []


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


    # --------------------------------------------------------
    # COD QUALITY / INTENT
    # --------------------------------------------------------

    cod_evidence = []

    if rto_rate is not None:

        cod_evidence.append(
            _evidence(
                metric=
                    "overall_rto_rate_percent",

                value=
                    rto_rate,

                source=
                    "d2c_logistics_engine",
            )
        )

    if cod:

        cod_evidence.append(
            _evidence(
                metric=
                    "cod_rto_rate_percent",

                value=
                    cod.get(
                        "rto_rate_percent"
                    ),

                source=
                    "d2c_logistics_engine",
            )
        )

    if prepaid:

        cod_evidence.append(
            _evidence(
                metric=
                    "prepaid_rto_rate_percent",

                value=
                    prepaid.get(
                        "rto_rate_percent"
                    ),

                source=
                    "d2c_logistics_engine",
            )
        )


    hypotheses.append(
        _hypothesis(
            hypothesis_id=
                "rto_cod_customer_intent",

            domain=
                "logistics",

            statement=(
                "Lower purchase intent or confirmation "
                "quality among COD orders may contribute "
                "to elevated COD RTO."
            ),

            related_claim=
                "cod_rto_signal",

            current_evidence=
                cod_evidence,

            missing_evidence=[
                _missing(
                    evidence_id=
                        "cod_confirmation_status",

                    description=(
                        "COD order-confirmation and "
                        "verification outcomes."
                    ),

                    reason=(
                        "Payment-mode association alone "
                        "cannot establish customer intent."
                    ),

                    suggested_source=
                        "cod_confirmation_events",
                ),

                _missing(
                    evidence_id=
                        "customer_rto_history",

                    description=(
                        "Historical RTO behaviour at "
                        "customer or cohort level."
                    ),

                    reason=(
                        "Needed to distinguish repeat "
                        "high-risk behaviour from payment "
                        "mode itself."
                    ),

                    suggested_source=
                        "customer_order_history",
                ),
            ],

            test=(
                "Compare verified vs unverified COD "
                "orders and customer RTO history."
            ),
        )
    )


    # --------------------------------------------------------
    # NDR / DELIVERY EXECUTION
    # --------------------------------------------------------

    ndr_evidence = []

    if ndr_rate is not None:

        ndr_evidence.append(
            _evidence(
                metric=
                    "ndr_rate_percent",

                value=
                    ndr_rate,

                source=
                    "d2c_logistics_engine",
            )
        )


    hypotheses.append(
        _hypothesis(
            hypothesis_id=
                "rto_ndr_execution",

            domain=
                "logistics",

            statement=(
                "Delivery-attempt or NDR-resolution "
                "inefficiency may contribute to RTO."
            ),

            related_claim=
                "overall_rto",

            current_evidence=
                ndr_evidence,

            missing_evidence=[
                _missing(
                    evidence_id=
                        "ndr_reason_codes",

                    description=(
                        "NDR reason codes and resolution "
                        "outcomes by order."
                    ),

                    reason=(
                        "The aggregate NDR rate does not "
                        "show which failure modes lead to "
                        "RTO."
                    ),

                    suggested_source=
                        "ndr_event_history",
                ),

                _missing(
                    evidence_id=
                        "attempt_sequence",

                    description=(
                        "Delivery-attempt sequence and "
                        "attempt outcomes."
                    ),

                    reason=(
                        "Required to measure whether "
                        "repeat-attempt execution affects "
                        "RTO probability."
                    ),

                    suggested_source=
                        "delivery_attempt_events",
                ),
            ],

            test=(
                "Measure RTO by NDR reason and delivery "
                "attempt sequence."
            ),
        )
    )


    # --------------------------------------------------------
    # COURIER / ZONE MIX
    # --------------------------------------------------------

    mix_evidence = []

    if couriers:

        mix_evidence.append(
            _evidence(
                metric=
                    "courier_count",

                value=
                    len(
                        couriers
                    ),

                source=
                    "d2c_logistics_engine",
            )
        )

    if zones:

        mix_evidence.append(
            _evidence(
                metric=
                    "zone_count",

                value=
                    len(
                        zones
                    ),

                source=
                    "d2c_logistics_engine",
            )
        )


    hypotheses.append(
        _hypothesis(
            hypothesis_id=
                "rto_mix_effect",

            domain=
                "logistics",

            statement=(
                "Courier or geographic mix may contribute "
                "to overall RTO performance."
            ),

            related_claim=
                "overall_rto",

            current_evidence=
                mix_evidence,

            missing_evidence=[
                _missing(
                    evidence_id=
                        "historical_courier_mix",

                    description=(
                        "Previous-period courier order mix "
                        "and RTO performance."
                    ),

                    reason=(
                        "Current courier performance cannot "
                        "show whether mix shifted toward "
                        "higher-risk couriers."
                    ),

                    suggested_source=
                        "courier_history",
                ),

                _missing(
                    evidence_id=
                        "historical_zone_mix",

                    description=(
                        "Previous-period geographic mix "
                        "and zone-level RTO."
                    ),

                    reason=(
                        "Required to determine whether "
                        "geographic mix deterioration "
                        "affected overall RTO."
                    ),

                    suggested_source=
                        "zone_history",
                ),
            ],

            test=(
                "Decompose overall RTO change into courier "
                "mix, zone mix and within-segment "
                "performance changes."
            ),
        )
    )


    return hypotheses


# ============================================================
# BUSINESS HEALTH
# ============================================================


def _build_business_health_hypotheses(
    context: dict,
):
    """
    Business Health composes a small set of material,
    still-unresolved hypotheses.

    It does not imply that these hypotheses are true.
    """

    revenue = (
        _build_revenue_hypotheses(
            context
        )
    )

    logistics = (
        _build_logistics_hypotheses(
            context
        )
    )

    preferred_ids = {
        "revenue_demand_weakness",
        "revenue_inventory_constraint",
        "rto_cod_customer_intent",
        "rto_ndr_execution",
    }

    combined = (
        revenue
        + logistics
    )

    return [
        item
        for item in combined
        if item.get(
            "hypothesis_id"
        )
        in preferred_ids
    ]


# ============================================================
# PUBLIC ENGINE
# ============================================================


def build_d2c_hypotheses(
    *,
    question_type: str,
    business_context: dict,
):
    """
    Build evidence-aware causal hypotheses.

    This engine never converts correlation into causation.

    A hypothesis must expose:
    - current evidence
    - missing evidence
    - test required to validate it
    - explicit causal guardrail
    """

    if question_type == "revenue":

        hypotheses = (
            _build_revenue_hypotheses(
                business_context
            )
        )

    elif question_type in {
        "logistics",
        "delivery",
    }:

        hypotheses = (
            _build_logistics_hypotheses(
                business_context
            )
        )

    elif question_type in {
        "business_health",
        "performance",
        "general_business",
        "general",
    }:

        hypotheses = (
            _build_business_health_hypotheses(
                business_context
            )
        )

    else:

        hypotheses = []


    status_counts = {
        "supported": 0,
        "insufficient_evidence": 0,
        "untested": 0,
    }


    for item in hypotheses:

        status = item.get(
            "status"
        )

        if status in status_counts:

            status_counts[
                status
            ] += 1


    missing_evidence_count = sum(
        len(
            item.get(
                "missing_evidence",
                [],
            )
        )
        for item in hypotheses
    )


    return make_json_safe({
        "status":
            "complete",

        "question_type":
            question_type,

        "hypotheses":
            hypotheses,

        "hypothesis_count":
            len(
                hypotheses
            ),

        "status_counts":
            status_counts,

        "missing_evidence_count":
            missing_evidence_count,

        "causal_guardrail": (
            "Hypotheses are possible explanations only. "
            "They must not be presented as established "
            "causes until the required evidence has been "
            "measured and validated."
        ),
    })

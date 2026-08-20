from backend.app.services.kpi_engine import (
    get_kpi_dashboard,
)
from backend.app.services.root_cause_engine import (
    analyze_root_causes,
)
from backend.app.services.insufficient_evidence import (
    evaluate_evidence_sufficiency,
)
from backend.app.services.financial_analysis import (
    get_monthly_revenue_analysis,
)


def _area_result(
    area: str,
    status: str,
    evidence=None,
    missing_data=None,
    message=None,
):
    """
    Build one standardized cross-functional result.
    """

    return {
        "area": area,
        "status": status,
        "evidence": (
            evidence
            if evidence is not None
            else []
        ),
        "missing_data": (
            missing_data
            if missing_data is not None
            else []
        ),
        "message": message,
    }


def investigate_marketing(month: str):
    """
    Marketing investigation.

    Current dataset does not contain marketing spend,
    traffic, CAC, ROAS or campaign data.
    """

    return _area_result(
        area="marketing",
        status="insufficient_data",
        missing_data=[
            "marketing spend",
            "traffic",
            "campaign data",
            "CAC",
            "ROAS",
            "channel acquisition data",
        ],
        message=(
            "Marketing performance cannot currently "
            "be evaluated from the available dataset."
        ),
    )


def investigate_customer(month: str):
    """
    Customer investigation.

    Current data contains customer IDs but does not
    yet support retention, cohorts, LTV or repeat-rate
    analysis in the analytical engine.
    """

    return _area_result(
        area="customer",
        status="insufficient_data",
        missing_data=[
            "repeat purchase analysis",
            "retention",
            "customer cohorts",
            "LTV",
            "customer segmentation",
        ],
        message=(
            "Customer behaviour cannot yet be evaluated "
            "deeply enough to establish a root cause."
        ),
    )


def investigate_product(month: str):
    """
    Product investigation.

    Product IDs exist, but product category, discount,
    COGS and product-mix analytics are not yet connected.
    """

    return _area_result(
        area="product",
        status="needs_investigation",
        missing_data=[
            "product category",
            "product mix",
            "discount data",
            "COGS",
            "product-level margin",
        ],
        message=(
            "Product-level data exists, but the current "
            "engine does not yet have enough product "
            "context to establish a product root cause."
        ),
    )


def investigate_pricing(month: str):
    """
    Pricing investigation.
    """

    return _area_result(
        area="pricing",
        status="insufficient_data",
        missing_data=[
            "historical list price",
            "discounts",
            "promotions",
            "realized selling price",
        ],
        message=(
            "Pricing impact cannot be separated from "
            "product mix with the current data."
        ),
    )


def investigate_operations(month: str):
    """
    Operational investigation using delivery and
    cancellation performance.
    """

    kpi = get_kpi_dashboard(month)

    delivery_rate = (
        kpi["delivery"]["rate_percent"]
    )

    cancellation_rate = (
        kpi["cancellation"]["rate_percent"]
    )

    evidence = [
        (
            f"Delivery rate was "
            f"{delivery_rate:.2f}%."
        ),
        (
            f"Cancellation rate was "
            f"{cancellation_rate:.2f}%."
        ),
    ]

    if (
        delivery_rate >= 95
        and cancellation_rate <= 2
    ):
        status = "healthy"

        message = (
            "Current operational metrics do not indicate "
            "a major fulfillment problem."
        )

    else:
        status = "problem_detected"

        message = (
            "Operational performance shows signals "
            "that require investigation."
        )

    return _area_result(
        area="operations",
        status=status,
        evidence=evidence,
        message=message,
    )


def investigate_logistics(month: str):
    """
    Logistics investigation using currently available
    freight and delivery data.
    """

    kpi = get_kpi_dashboard(month)

    freight = kpi[
        "freight"
    ]["value"]

    delivery_rate = kpi[
        "delivery"
    ]["rate_percent"]

    return _area_result(
        area="logistics",
        status="partial_evidence",
        evidence=[
            (
                f"Freight value was "
                f"{freight:.2f}."
            ),
            (
                f"Delivery rate was "
                f"{delivery_rate:.2f}%."
            ),
        ],
        missing_data=[
            "courier",
            "region",
            "RTO",
            "COD vs prepaid",
            "delivery TAT",
            "pin-code performance",
        ],
        message=(
            "Basic logistics performance is available, "
            "but detailed logistics root-cause analysis "
            "requires courier, region and RTO data."
        ),
    )


def investigate_inventory(month: str):
    """
    Inventory investigation.
    """

    return _area_result(
        area="inventory",
        status="insufficient_data",
        missing_data=[
            "inventory levels",
            "stockouts",
            "days of inventory",
            "SKU availability",
            "purchase orders",
        ],
        message=(
            "Inventory availability cannot currently "
            "be evaluated."
        ),
    )


def investigate_finance(month: str):
    """
    Finance investigation.

    Revenue and freight are available, but full profit
    analysis is impossible without COGS and other costs.
    """

    financial = (
        get_monthly_revenue_analysis(
            month
        )
    )

    evidence = [
        (
            f"Revenue was "
            f"{financial['revenue']:.2f}."
        ),
        (
            f"Freight value was "
            f"{financial['freight_value']:.2f}."
        ),
    ]

    return _area_result(
        area="finance",
        status="partial_evidence",
        evidence=evidence,
        missing_data=[
            "COGS",
            "payment fees",
            "marketing cost",
            "returns cost",
            "RTO cost",
            "gross profit",
            "contribution margin",
        ],
        message=(
            "Revenue and freight can be evaluated, "
            "but profitability cannot yet be established."
        ),
    )


def build_cross_functional_investigation(
    month: str
):
    """
    Investigate the same business problem across
    multiple business functions.

    This prevents ProfitLens from assuming a root cause
    belongs to one function without evidence.
    """

    root_cause = analyze_root_causes(
        month
    )

    sufficiency = (
        evaluate_evidence_sufficiency(
            month
        )
    )

    functions = [
        investigate_marketing(month),
        investigate_product(month),
        investigate_pricing(month),
        investigate_customer(month),
        investigate_operations(month),
        investigate_logistics(month),
        investigate_inventory(month),
        investigate_finance(month),
    ]

    problem_areas = [
        item
        for item in functions
        if item["status"]
        == "problem_detected"
    ]

    healthy_areas = [
        item
        for item in functions
        if item["status"]
        == "healthy"
    ]

    evidence_gaps = [
        item
        for item in functions
        if item["status"]
        in {
            "insufficient_data",
            "partial_evidence",
            "needs_investigation",
        }
    ]

    return {
        "period": month,

        "status": "complete",

        "primary_measured_driver": (
            root_cause.get(
                "measured_drivers",
                [{}]
            )[0].get(
                "driver"
            )
            if root_cause.get(
                "measured_drivers"
            )
            else None
        ),

        "evidence_sufficiency": (
            sufficiency["status"]
        ),

        "functions": functions,

        "summary": {
            "problem_areas": [
                item["area"]
                for item in problem_areas
            ],

            "healthy_areas": [
                item["area"]
                for item in healthy_areas
            ],

            "evidence_gap_areas": [
                item["area"]
                for item in evidence_gaps
            ],
        },

        "conclusion": (
            "ProfitLens has evaluated the current problem "
            "across multiple business functions. Areas with "
            "insufficient evidence are not treated as confirmed "
            "root causes."
        ),
    }
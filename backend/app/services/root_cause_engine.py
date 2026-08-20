from backend.app.services.driver_analysis import (
    analyze_revenue_change,
)
from backend.app.services.kpi_engine import (
    get_kpi_dashboard,
)


def analyze_root_causes(month: str):
    """
    Build a structured explanation of business performance.

    The engine separates:

    - observed facts
    - measured drivers
    - hypotheses
    - insufficient evidence
    """

    driver_analysis = analyze_revenue_change(
        month
    )

    kpi = get_kpi_dashboard(month)

    # ---------------------------------------------
    # HANDLE INSUFFICIENT DATA
    # ---------------------------------------------

    if driver_analysis.get(
        "status"
    ) != "complete":

        return {
            "month": month,
            "status": "insufficient_data",
            "observed_facts": [],
            "measured_drivers": [],
            "hypotheses": [],
            "unknowns": [
                driver_analysis.get(
                    "message",
                    "Insufficient data available."
                )
            ],
            "primary_explanation": (
                "There is insufficient historical data "
                "to determine the measurable drivers."
            )
        }

    # ---------------------------------------------
    # OBSERVED FACTS
    # ---------------------------------------------

    observed_facts = []

    revenue_change = driver_analysis[
        "revenue_change"
    ]

    if revenue_change < 0:

        observed_facts.append(
            f"Revenue declined by "
            f"{abs(revenue_change):.2f} "
            f"compared with the previous month."
        )

    elif revenue_change > 0:

        observed_facts.append(
            f"Revenue increased by "
            f"{abs(revenue_change):.2f} "
            f"compared with the previous month."
        )

    else:

        observed_facts.append(
            "Revenue remained unchanged compared "
            "with the previous month."
        )

    # ---------------------------------------------
    # ADD KPI OBSERVATIONS
    # ---------------------------------------------

    orders = kpi["orders"]

    if orders["growth_percent"] is not None:

        if orders["growth_percent"] < 0:

            observed_facts.append(
                f"Orders declined by "
                f"{abs(orders['growth_percent']):.2f}%."
            )

        elif orders["growth_percent"] > 0:

            observed_facts.append(
                f"Orders increased by "
                f"{orders['growth_percent']:.2f}%."
            )

    aov = kpi["aov"]

    if aov["growth_percent"] is not None:

        if aov["growth_percent"] < 0:

            observed_facts.append(
                f"AOV declined by "
                f"{abs(aov['growth_percent']):.2f}%."
            )

        elif aov["growth_percent"] > 0:

            observed_facts.append(
                f"AOV increased by "
                f"{aov['growth_percent']:.2f}%."
            )

    # ---------------------------------------------
    # MEASURED DRIVERS
    # ---------------------------------------------

    measured_drivers = []

    drivers = driver_analysis["drivers"]

    primary_driver = driver_analysis[
        "primary_driver"
    ]

    primary_effect = drivers[
        primary_driver
    ]["effect"]

    if primary_driver == "order_volume":

        measured_drivers.append({
            "driver": "order_volume",
            "effect": primary_effect,
            "explanation": (
                "Changes in order volume had the "
                "largest measurable impact on revenue."
            )
        })

    elif primary_driver == "aov":

        measured_drivers.append({
            "driver": "aov",
            "effect": primary_effect,
            "explanation": (
                "Changes in average order value had "
                "the largest measurable impact on revenue."
            )
        })

    else:

        measured_drivers.append({
            "driver": "interaction",
            "effect": primary_effect,
            "explanation": (
                "The combined change in order volume "
                "and average order value had the largest "
                "measurable impact."
            )
        })

    # Add secondary drivers

    for driver_name, driver_data in drivers.items():

        if driver_name == primary_driver:
            continue

        effect = driver_data["effect"]

        if effect != 0:

            measured_drivers.append({
                "driver": driver_name,
                "effect": effect,
                "explanation": (
                    f"{driver_name.replace('_', ' ').title()} "
                    f"also contributed to the revenue change."
                )
            })

    # ---------------------------------------------
    # HYPOTHESES
    #
    # These are intentionally NOT stated as facts.
    # ---------------------------------------------

    hypotheses = []

    if primary_driver == "order_volume":

        hypotheses.append({
            "hypothesis": (
                "The decline in orders may be related "
                "to weaker customer demand or acquisition."
            ),
            "confidence": "unverified",
            "required_evidence": [
                "traffic data",
                "conversion data",
                "marketing spend",
                "customer acquisition data"
            ]
        })

    elif primary_driver == "aov":

        hypotheses.append({
            "hypothesis": (
                "The decline in AOV may be related to "
                "changes in product mix, pricing or "
                "customer purchasing behaviour."
            ),
            "confidence": "unverified",
            "required_evidence": [
                "product category data",
                "pricing data",
                "discount data",
                "customer basket data"
            ]
        })

    # ---------------------------------------------
    # OPERATIONAL CONTEXT
    # ---------------------------------------------

    delivery_rate = kpi["delivery"][
        "rate_percent"
    ]

    cancellation_rate = kpi["cancellation"][
        "rate_percent"
    ]

    observed_facts.append(
        f"Delivery rate was {delivery_rate:.2f}%."
    )

    observed_facts.append(
        f"Cancellation rate was "
        f"{cancellation_rate:.2f}%."
    )

    # ---------------------------------------------
    # UNKNOWN / MISSING EVIDENCE
    # ---------------------------------------------

    unknowns = [
        "The available data cannot determine "
        "whether marketing performance caused "
        "the order change.",

        "The available data cannot determine "
        "whether pricing changes caused the "
        "AOV change.",

        "Customer-level behaviour data is required "
        "to determine whether customer demand "
        "changed."
    ]

    # ---------------------------------------------
    # PRIMARY EXPLANATION
    # ---------------------------------------------

    primary_explanation = (
        f"The strongest measurable explanation for "
        f"the revenue change is {primary_driver.replace('_', ' ')}, "
        f"which contributed an estimated "
        f"{abs(primary_effect):.2f} "
        f"to the revenue movement."
    )

    return {
        "month": month,
        "status": "complete",
        "observed_facts": observed_facts,
        "measured_drivers": measured_drivers,
        "hypotheses": hypotheses,
        "unknowns": unknowns,
        "primary_explanation": primary_explanation,
    }
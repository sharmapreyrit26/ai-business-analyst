from backend.app.services.question_router import classify_question
from backend.app.services.fast_analysis import execute_fast_analysis
from backend.app.services.llm_service import ask_business_analyst


def _build_fast_fallback(
    question_type: str,
    month: str,
    context: dict,
) -> dict:
    """
    Build a deterministic answer when the external
    AI service is unavailable or times out.
    """

    # --------------------------------------------------
    # REVENUE
    # --------------------------------------------------

    if question_type == "revenue":

        revenue = context.get(
            "revenue_analysis",
            {}
        )

        driver = context.get(
            "driver_analysis",
            {}
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
                    "Not established"
                )
            ),
            "recommended_actions": [],
        }

    # --------------------------------------------------
    # ORDERS
    # --------------------------------------------------

    if question_type == "orders":

        orders = context.get(
            "orders",
            {}
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

    # --------------------------------------------------
    # DELIVERY
    # --------------------------------------------------

    if question_type == "delivery":

        delivery = context.get(
            "delivery",
            {}
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

    # --------------------------------------------------
    # CANCELLATION
    # --------------------------------------------------

    if question_type == "cancellation":

        cancellation = context.get(
            "cancellation",
            {}
        )

        return {
            "answer": (
                f"Cancellation rate was "
                f"{cancellation.get('rate_percent')}% "
                f"in {month}."
            ),
            "evidence": [
                (
                    f"Cancelled orders: "
                    f"{cancellation.get('cancelled_orders')}."
                )
            ],
            "likely_driver": "Not established",
            "recommended_actions": [],
        }

    # --------------------------------------------------
    # PRODUCT
    # --------------------------------------------------

    if question_type == "product":

        product_analysis = context.get(
            "product_analysis",
            {}
        )

        products = product_analysis.get(
            "top_products",
            []
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
                    (
                        f"Revenue share: "
                        f"{product.get('revenue_share_percent')}%."
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

    # --------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------

    if question_type == "customer":

        customer = context.get(
            "customer_analysis",
            {}
        )

        repeat_purchase = (
            customer
            .get("unavailable_analysis", {})
            .get("repeat_purchase", {})
        )

        return {
            "answer": (
                "Reliable repeat-purchase and retention "
                "metrics cannot currently be calculated "
                "with the connected customer data."
            ),
            "evidence": [
                repeat_purchase.get(
                    "reason",
                    (
                        "Persistent customer identity "
                        "data is unavailable."
                    ),
                )
            ],
            "likely_driver": (
                "Insufficient customer identity data"
            ),
            "recommended_actions": [
                (
                    "Connect persistent customer identity "
                    "data before calculating retention, "
                    "cohorts or LTV."
                )
            ],
        }

    # --------------------------------------------------
    # LOGISTICS
    # --------------------------------------------------

    if question_type == "logistics":

        logistics = context.get(
            "logistics_analysis",
            {}
        )

        delivery = (
            logistics
            .get("fulfilment_tat", {})
            .get("purchase_to_delivery", {})
        )

        promise = logistics.get(
            "delivery_promise",
            {}
        )

        average = delivery.get(
            "average"
        )

        p90 = delivery.get(
            "p90"
        )

        evidence = []

        if average is not None:
            evidence.append(
                f"Average purchase-to-delivery TAT: "
                f"{average} days."
            )

        if p90 is not None:
            evidence.append(
                f"P90 purchase-to-delivery TAT: "
                f"{p90} days."
            )

        if (
            promise.get(
                "on_time_delivery_percent"
            )
            is not None
        ):
            evidence.append(
                f"On-time delivery rate: "
                f"{promise.get('on_time_delivery_percent')}%."
            )

        return {
            "answer": (
                f"P90 purchase-to-delivery TAT was "
                f"{p90} days."
                if p90 is not None
                else (
                    f"Average purchase-to-delivery TAT "
                    f"was {average} days."
                    if average is not None
                    else (
                        "Delivery TAT could not be "
                        "calculated."
                    )
                )
            ),
            "evidence": evidence,
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    # --------------------------------------------------
    # SCENARIO
    # --------------------------------------------------

    if question_type == "scenario":

        scenario = context.get(
            "scenario_analysis",
            {}
        )

        if (
            scenario.get("status")
            != "complete"
        ):

            return {
                "answer": (
                    "The requested scenario could not "
                    "be executed with the supplied "
                    "parameters."
                ),
                "evidence": [],
                "likely_driver": "Not applicable",
                "recommended_actions": [],
            }

        result = scenario.get(
            "scenario_result",
            {}
        )

        scenario_result = result.get(
            "scenario_result",
            {}
        )

        difference = result.get(
            "difference",
            {}
        )

        return {
            "answer": (
                f"The scenario produces estimated "
                f"revenue of "
                f"{scenario_result.get('revenue')}, "
                f"with an incremental revenue impact "
                f"of "
                f"{difference.get('incremental_revenue')}."
            ),
            "evidence": [
                (
                    f"Scenario type: "
                    f"{scenario.get('scenario_type')}."
                )
            ],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    # --------------------------------------------------
    # GENERAL / BUSINESS HEALTH
    # --------------------------------------------------

    kpi = context.get(
        "kpi_dashboard",
        {}
    )

    revenue_analysis = context.get(
        "revenue_analysis",
        {}
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
            (
                f"Cancellation rate: "
                f"{kpi.get('cancellation', {}).get('rate_percent')}%."
            ),
        ]

    return {
        "answer": (
            f"Business analysis was completed "
            f"for {month}. Revenue changed by "
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
            .get("driver_analysis", {})
            .get(
                "primary_driver",
                "Not established"
            )
        ),
        "recommended_actions": [],
    }


def answer_business_question(
    question: str,
    month: str = "2018-06",
) -> dict:
    """
    Fast interactive ProfitLens Business Analyst.

    Flow:
    1. Classify question.
    2. Run one focused deterministic analysis.
    3. Ask the LLM to interpret the evidence.
    4. Fall back to deterministic output on timeout/error.
    """

    question_type = classify_question(
        question
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

        answer = _build_fast_fallback(
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

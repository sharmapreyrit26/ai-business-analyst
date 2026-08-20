from fastapi import APIRouter, HTTPException

from backend.app.schemas import (
    BusinessQuestionRequest,
    BusinessQuestionResponse,
    ProductAnalyticsResponse,
    CustomerAnalyticsResponse,
    LogisticsAnalyticsResponse,
    ScenarioRequest,
    ScenarioResponse,
    AnalysisPlanRequest,
    AnalysisPlanResponse,
)

from backend.app.services.business_analyst import (
    answer_business_question,
)

from backend.app.services.product_analysis import (
    get_product_analytics,
)

from backend.app.services.customer import (
    get_customer_analytics,
)

from backend.app.services.logistics_analysis import (
    get_logistics_analytics,
)

from backend.app.services.scenario_executor import (
    execute_scenario_question,
)

from backend.app.services.analysis_executor import (
    execute_analysis_plan,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ============================================================
# AI BUSINESS ANALYST
# ============================================================


@router.post(
    "/business-question",
    response_model=BusinessQuestionResponse,
)
def business_question(
    request: BusinessQuestionRequest,
):
    """
    Ask ProfitLens a natural-language business question.

    Flow:
    - classify question
    - create analysis plan
    - execute deterministic analytics
    - interpret results
    - fall back to deterministic response if AI is unavailable
    """

    try:

        return answer_business_question(
            question=request.question,
            month=request.month,
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ============================================================
# PRODUCT ANALYTICS
# ============================================================


@router.get(
    "/products/{month}",
    response_model=ProductAnalyticsResponse,
)
def product_analytics(
    month: str,
):
    """
    Return product-level analytics for a selected month.

    Available:
    - product revenue
    - units sold
    - orders
    - average selling price
    - freight burden
    - revenue share
    - revenue concentration

    True product profitability is not calculated
    until COGS and variable costs are available.
    """

    try:

        return get_product_analytics(
            month=month
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ============================================================
# CUSTOMER ANALYTICS
# ============================================================


@router.get(
    "/customers",
    response_model=CustomerAnalyticsResponse,
)
def customer_analytics():
    """
    Return currently available customer analytics.

    The API explicitly reports customer metrics that
    cannot be calculated because required data is missing.
    """

    try:

        return get_customer_analytics()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ============================================================
# LOGISTICS ANALYTICS
# ============================================================


@router.get(
    "/logistics/{month}",
    response_model=LogisticsAnalyticsResponse,
)
def logistics_analytics(
    month: str,
):
    """
    Return logistics and fulfilment analytics.

    Includes:
    - purchase-to-approval TAT
    - approval-to-carrier TAT
    - carrier-to-delivery TAT
    - purchase-to-delivery TAT
    - average / median / P90
    - on-time delivery
    - late delivery
    - promised-delivery performance
    """

    try:

        return get_logistics_analytics(
            month=month
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ============================================================
# SCENARIO / WHAT-IF ANALYSIS
# ============================================================


@router.post(
    "/scenario",
    response_model=ScenarioResponse,
)
def scenario_analysis(
    request: ScenarioRequest,
):
    """
    Execute a deterministic natural-language
    what-if scenario.

    Example:

    What if AOV increases by 12%?

    or:

    What happens if we recover half of lost orders?
    """

    try:

        return execute_scenario_question(
            question=request.question,
            month=request.month,
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ============================================================
# ANALYSIS PLAN + EXECUTION
# ============================================================


@router.post(
    "/analysis-plan",
    response_model=AnalysisPlanResponse,
)
def analysis_plan(
    request: AnalysisPlanRequest,
):
    """
    Build and execute the deterministic analytical
    plan required to answer a business question.

    This endpoint is especially useful for:
    - debugging
    - auditability
    - showing how ProfitLens reached a conclusion
    - future analyst/admin interfaces
    """

    try:

        return execute_analysis_plan(
            question=request.question,
            month=request.month,
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error
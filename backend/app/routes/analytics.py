from fastapi import (
    APIRouter,
    HTTPException,
)

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

from backend.app.exceptions import (
    InvalidRequestError,
    ResourceNotFoundError,
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

from backend.app.services.financial_analysis import (
    get_monthly_revenue,
    get_monthly_data_quality,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ============================================================
# ERROR MAPPING
# ============================================================


def _raise_http_error(
    error: Exception,
):
    """
    Convert expected ProfitLens errors into
    appropriate HTTP responses.

    Known client/data errors:
    - 400 for invalid requests
    - 404 for unavailable resources

    Unexpected errors:
    - 500
    """

    if isinstance(
        error,
        InvalidRequestError,
    ):
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    if isinstance(
        error,
        ResourceNotFoundError,
    ):
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    if isinstance(
        error,
        ValueError,
    ):
        message = str(
            error
        )

        normalized = (
            message.lower()
        )

        if (
            "not found"
            in normalized
            or "no performance data"
            in normalized
            or "no data"
            in normalized
        ):
            raise HTTPException(
                status_code=404,
                detail=message,
            ) from error

        raise HTTPException(
            status_code=400,
            detail=message,
        ) from error

    raise HTTPException(
        status_code=500,
        detail=(
            "An unexpected server error occurred."
        ),
    ) from error


# ============================================================
# REPORTING PERIODS
# ============================================================


@router.get(
    "/reporting-periods",
)
def reporting_periods():
    """
    Return reporting months available in the
    connected dataset.

    The newest complete reporting month is used
    as the default month.
    """

    try:
        monthly = get_monthly_revenue()

        if monthly.empty:
            return {
                "months": [],
                "complete_months": [],
                "partial_months": [],
                "default_month": None,
            }

        months = (
            monthly["month"]
            .astype(str)
            .dropna()
            .unique()
            .tolist()
        )

        months = sorted(
            months,
            reverse=True,
        )

        quality = (
            get_monthly_data_quality()
        )

        quality_by_month = {
            item["month"]: item
            for item in quality
        }

        complete_months = [
            month
            for month in months
            if (
                quality_by_month
                .get(
                    month,
                    {}
                )
                .get(
                    "data_quality"
                )
                == "complete"
            )
        ]

        partial_months = [
            month
            for month in months
            if (
                quality_by_month
                .get(
                    month,
                    {}
                )
                .get(
                    "data_quality"
                )
                == "partial"
            )
        ]

        default_month = (
            complete_months[0]
            if complete_months
            else (
                months[0]
                if months
                else None
            )
        )

        return {
            "months": months,
            "complete_months": complete_months,
            "partial_months": partial_months,
            "default_month": default_month,
        }

    except Exception as error:
        _raise_http_error(
            error
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
    - classify the question
    - execute focused deterministic analytics
    - interpret the result
    - fall back to deterministic output if AI is unavailable
    """

    try:
        return answer_business_question(
            question=request.question,
            month=request.month,
        )

    except Exception as error:
        _raise_http_error(
            error
        )


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

    True product profitability remains unavailable
    until COGS and variable-cost data are connected.
    """

    try:
        return get_product_analytics(
            month=month
        )

    except Exception as error:
        _raise_http_error(
            error
        )


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

    Metrics that cannot be calculated because of
    missing customer identity or cost data are
    explicitly marked unavailable.
    """

    try:
        return get_customer_analytics()

    except Exception as error:
        _raise_http_error(
            error
        )


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
    - fulfilment TAT
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
        _raise_http_error(
            error
        )


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
    - What if AOV increases by 12%?
    - What happens if we recover half of lost orders?
    """

    try:
        return execute_scenario_question(
            question=request.question,
            month=request.month,
        )

    except Exception as error:
        _raise_http_error(
            error
        )


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

    This endpoint is useful for:
    - debugging
    - auditability
    - deep investigation
    - future analyst/admin interfaces
    """

    try:
        return execute_analysis_plan(
            question=request.question,
            month=request.month,
        )

    except Exception as error:
        _raise_http_error(
            error
        )
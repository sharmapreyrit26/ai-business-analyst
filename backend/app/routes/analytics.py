

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
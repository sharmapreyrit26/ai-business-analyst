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


@router.post(
    "/business-question",
    response_model=BusinessQuestionResponse,
)
def business_question(
    request: BusinessQuestionRequest,
):
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


@router.get(
    "/products/{month}",
    response_model=ProductAnalyticsResponse,
)
def product_analytics(
    month: str,
):
    try:
        return get_product_analytics(
            month=month
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@router.get(
    "/customers",
    response_model=CustomerAnalyticsResponse,
)
def customer_analytics():
    try:
        return get_customer_analytics()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@router.get(
    "/logistics/{month}",
    response_model=LogisticsAnalyticsResponse,
)
def logistics_analytics(
    month: str,
):
    try:
        return get_logistics_analytics(
            month=month
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@router.post(
    "/scenario",
    response_model=ScenarioResponse,
)
def scenario_analysis(
    request: ScenarioRequest,
):
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


@router.post(
    "/analysis-plan",
    response_model=AnalysisPlanResponse,
)
def analysis_plan(
    request: AnalysisPlanRequest,
):
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

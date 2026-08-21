from fastapi import (
    APIRouter,
    HTTPException,
)

from backend.app.schemas import (
    BusinessQuestionRequest,
    BusinessQuestionResponse,
    ScenarioRequest,
    ScenarioResponse,
)

from backend.app.exceptions import (
    InvalidRequestError,
    ResourceNotFoundError,
)

from backend.app.services.business_analyst import (
    answer_business_question,
)

from backend.app.services.scenario_executor import (
    execute_scenario_question,
)


router = APIRouter(
    prefix="/analytics",
    tags=[
        "ProfitLens Intelligence",
    ],
)


# ============================================================
# ERROR MAPPING
# ============================================================


def _raise_http_error(
    error: Exception,
):
    """
    Convert expected ProfitLens errors into
    HTTP responses.
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
            "not found" in normalized
            or "no performance data"
            in normalized
            or "no data" in normalized
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
# ASK PROFITLENS
# ============================================================


@router.post(
    "/business-question",
    response_model=BusinessQuestionResponse,
)
def business_question(
    request: BusinessQuestionRequest,
):
    """
    Ask ProfitLens a natural-language
    business question.

    D2C deterministic analytics own all
    numerical business truth.

    AI is used only for interpretation.
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
# SCENARIO LAB
# ============================================================


@router.post(
    "/scenario",
    response_model=ScenarioResponse,
)
def scenario_analysis(
    request: ScenarioRequest,
):
    """
    Run a deterministic ProfitLens sensitivity
    scenario.

    Scenario calculations are performed by the
    deterministic scenario engine.
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
from fastapi import (
    APIRouter,
    HTTPException,
)

from backend.app.schemas import (
    AnalysisPlanRequest,
    AnalysisPlanResponse,
)

from backend.app.exceptions import (
    InvalidRequestError,
    ResourceNotFoundError,
)

router = APIRouter(
    prefix="/internal",
    tags=["Internal"],
)


def _raise_http_error(
    error: Exception,
):
    """
    Map expected ProfitLens errors to HTTP responses.

    This router is intended for debugging,
    auditability and future internal tooling.
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
            or "no performance data" in normalized
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


@router.post(
    "/analysis-plan",
    response_model=AnalysisPlanResponse,
)
def analysis_plan(
    request: AnalysisPlanRequest,
):
    """
    Execute an internal deterministic analysis plan.

    Intended for:
    - debugging
    - auditability
    - development
    - future analyst/admin tooling

    This endpoint is not used by the
    production ProfitLens frontend.
    """

    try:
        # Lazy import: the legacy/deep-analysis stack is loaded
        # only when this internal endpoint is explicitly used.
        from backend.app.services.analysis_executor import (
            execute_analysis_plan,
        )

        return execute_analysis_plan(
            question=request.question,
            month=request.month,
        )

    except Exception as error:
        _raise_http_error(
            error
        )

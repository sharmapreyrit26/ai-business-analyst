from copy import deepcopy
from functools import lru_cache

from fastapi import APIRouter

from backend.app.services.kpi_engine import (
    get_kpi_dashboard,
)

from backend.app.services.financial_analysis import (
    get_monthly_revenue,
    get_monthly_data_quality,
)

from backend.app.services.insight_engine import (
    generate_business_insights,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@lru_cache(maxsize=24)
def _build_dashboard_cached(
    month: str,
):
    """
    Build and cache the complete dashboard response.

    The current Olist datasets are static while the
    application process is running, so recalculating
    the same month on every browser refresh is wasteful.

    Cache is automatically cleared whenever the
    backend process restarts.
    """

    kpis = get_kpi_dashboard(
        month
    )

    monthly_revenue = (
        get_monthly_revenue()
        .to_dict(
            orient="records"
        )
    )

    data_quality = (
        get_monthly_data_quality()
    )

    insights = (
        generate_business_insights(
            month
        )
    )

    return {
        "month": month,

        "kpis": kpis,

        "monthly_revenue": (
            monthly_revenue
        ),

        "data_quality": (
            data_quality
        ),

        "insights": (
            insights
        ),
    }


@router.get("/{month}")
def get_dashboard(
    month: str = "2018-06",
):
    """
    Return the ProfitLens dashboard for a
    selected reporting month.

    A deep copy is returned so API consumers
    cannot accidentally mutate the cached object.
    """

    return deepcopy(
        _build_dashboard_cached(
            month
        )
    )
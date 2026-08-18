from fastapi import APIRouter

from backend.app.services.kpi_engine import get_kpi_dashboard
from backend.app.services.financial_analysis import (
    get_monthly_revenue,
    get_monthly_data_quality,
)
from backend.app.services.insight_engine import (
    generate_business_insights,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/{month}")
def get_dashboard(month: str = "2018-06"):

    kpis = get_kpi_dashboard(month)

    monthly_revenue = (
        get_monthly_revenue()
        .to_dict(orient="records")
    )

    data_quality = get_monthly_data_quality()

    insights = generate_business_insights(month)

    return {
        "month": month,
        "kpis": kpis,
        "monthly_revenue": monthly_revenue,
        "data_quality": data_quality,
        "insights": insights,
    }
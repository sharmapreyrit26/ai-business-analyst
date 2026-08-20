from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# COMMON
# ============================================================


class DataQualityStatus(BaseModel):
    status: Optional[str] = None
    is_partial_month: Optional[bool] = None


class AnalysisExecutionSummary(BaseModel):
    total_steps: int
    successful_steps: int
    failed_steps: int


# ============================================================
# KPI MODELS
# ============================================================


class MetricComparison(BaseModel):
    value: Optional[float] = None
    previous_value: Optional[float] = None
    growth_percent: Optional[float] = None


class OrderMetricComparison(BaseModel):
    value: Optional[int] = None
    previous_value: Optional[int] = None
    growth_percent: Optional[float] = None


class DeliveryMetric(BaseModel):
    rate_percent: Optional[float] = None
    delivered_orders: Optional[int] = None


class CancellationMetric(BaseModel):
    rate_percent: Optional[float] = None
    cancelled_orders: Optional[int] = None


class ValueMetric(BaseModel):
    value: Optional[float] = None


class IntegerValueMetric(BaseModel):
    value: Optional[int] = None


class BusinessTotals(BaseModel):
    total_orders: Optional[int] = None
    delivered_orders: Optional[int] = None
    cancelled_orders: Optional[int] = None


class KPIDashboard(BaseModel):
    month: str

    data_quality: dict[str, Any]

    revenue: MetricComparison

    orders: OrderMetricComparison

    aov: MetricComparison

    delivery: DeliveryMetric

    cancellation: CancellationMetric

    freight: ValueMetric

    items: IntegerValueMetric

    business_totals: BusinessTotals


# ============================================================
# AI BUSINESS ANALYST
# ============================================================


class BusinessAnswer(BaseModel):
    answer: str

    evidence: list[str] = Field(
        default_factory=list
    )

    likely_driver: str

    recommended_actions: list[str] = Field(
        default_factory=list
    )


class BusinessQuestionRequest(BaseModel):
    question: str

    month: str = "2018-06"


class BusinessQuestionResponse(BaseModel):
    question: str

    month: str

    question_type: str

    analysis_execution: Optional[
        AnalysisExecutionSummary
    ] = None

    ai_available: bool

    answer: BusinessAnswer


# ============================================================
# DASHBOARD
# ============================================================


class DashboardResponse(BaseModel):
    month: str

    kpis: KPIDashboard

    monthly_revenue: list[
        dict[str, Any]
    ]

    data_quality: list[
        dict[str, Any]
    ]

    insights: dict[
        str,
        Any
    ]


# ============================================================
# PRODUCT
# ============================================================


class ProductAnalyticsResponse(BaseModel):
    month: Optional[str] = None

    summary: dict[
        str,
        Any
    ]

    top_products: list[
        dict[str, Any]
    ]

    concentration: dict[
        str,
        Any
    ]

    available_metrics: list[str]

    unavailable_metrics: dict[
        str,
        Any
    ]


# ============================================================
# CUSTOMER
# ============================================================


class CustomerAnalyticsResponse(BaseModel):
    status: str

    data_quality: dict[
        str,
        Any
    ]

    available_analysis: dict[
        str,
        Any
    ]

    unavailable_analysis: dict[
        str,
        Any
    ]

    next_data_requirement: dict[
        str,
        Any
    ]


# ============================================================
# LOGISTICS
# ============================================================


class LogisticsAnalyticsResponse(BaseModel):
    month: Optional[str] = None

    fulfilment_tat: dict[
        str,
        Any
    ]

    delivery_promise: dict[
        str,
        Any
    ]

    order_status: dict[
        str,
        Any
    ]

    data_quality: dict[
        str,
        Any
    ]

    available_metrics: list[str]

    unavailable_metrics: dict[
        str,
        Any
    ]


# ============================================================
# SCENARIO
# ============================================================


class ScenarioRequest(BaseModel):
    question: str

    month: str = "2018-06"


class ScenarioResponse(BaseModel):
    question: str

    month: str

    status: str

    scenario_type: Optional[str] = None

    parameters: Optional[
        dict[str, Any]
    ] = None

    parser_result: Optional[
        dict[str, Any]
    ] = None

    scenario_result: Optional[
        dict[str, Any]
    ] = None


# ============================================================
# ANALYSIS PLAN
# ============================================================


class AnalysisPlanRequest(BaseModel):
    question: str

    month: str = "2018-06"


class AnalysisPlanResponse(BaseModel):
    question: str

    month: str

    question_type: str

    total_steps: int

    successful_steps: int

    failed_steps: int

    analysis_plan: list[
        dict[str, Any]
    ]

    execution_results: list[
        dict[str, Any]
    ]


# ============================================================
# HEALTH
# ============================================================


class HealthResponse(BaseModel):
    status: str
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ============================================================
# DATE RANGE
# ============================================================


class DateRange(BaseModel):
    start_date: str
    end_date: str


# ============================================================
# COMPARISON
# ============================================================


class ComparisonPeriod(BaseModel):
    mode: Literal[
        "none",
        "previous_period",
        "previous_month",
        "previous_year",
        "custom",
    ] = "previous_period"

    start_date: Optional[str] = None
    end_date: Optional[str] = None


# ============================================================
# GLOBAL FILTERS
# ============================================================


class AnalyticsFilters(BaseModel):
    channels: list[str] = Field(
        default_factory=list
    )

    categories: list[str] = Field(
        default_factory=list
    )

    skus: list[str] = Field(
        default_factory=list
    )

    couriers: list[str] = Field(
        default_factory=list
    )

    warehouses: list[str] = Field(
        default_factory=list
    )

    payment_methods: list[str] = Field(
        default_factory=list
    )

    states: list[str] = Field(
        default_factory=list
    )

    zones: list[str] = Field(
        default_factory=list
    )


# ============================================================
# GLOBAL ANALYTICS CONTEXT
# ============================================================


class AnalyticsContext(BaseModel):
    """
    Shared ProfitLens analytics context.

    This becomes the common contract used by:
    - dashboards
    - charts
    - tables
    - AI Analyst
    - investigations
    - Scenario Lab
    - exports

    Existing month-based endpoints can continue operating
    during the migration.
    """

    workspace_id: Optional[str] = None
    brand_id: Optional[str] = None

    period: DateRange

    comparison: ComparisonPeriod = Field(
        default_factory=ComparisonPeriod
    )

    filters: AnalyticsFilters = Field(
        default_factory=AnalyticsFilters
    )

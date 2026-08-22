from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# ENUMS
# ============================================================


class MetricUnit(str, Enum):
    currency = "currency"
    percent = "percent"
    ratio = "ratio"
    count = "count"
    days = "days"
    decimal = "decimal"


class MetricDirection(str, Enum):
    up = "up"
    down = "down"
    flat = "flat"
    unknown = "unknown"


class MetricSentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"
    warning = "warning"
    unknown = "unknown"


class MetricQuality(str, Enum):
    verified = "verified"
    partial = "partial"
    estimated = "estimated"
    unavailable = "unavailable"


# ============================================================
# METRIC SOURCE
# ============================================================


class MetricSource(BaseModel):
    engine: Optional[str] = None

    tables: list[str] = Field(
        default_factory=list
    )

    fields: list[str] = Field(
        default_factory=list
    )


# ============================================================
# METRIC COMPARISON
# ============================================================


class MetricComparison(BaseModel):
    previous_value: Optional[float] = None

    change_absolute: Optional[float] = None

    change_percent: Optional[float] = None

    direction: MetricDirection = (
        MetricDirection.unknown
    )


# ============================================================
# METRIC CONTRACT
# ============================================================


class MetricContract(BaseModel):
    """
    Canonical ProfitLens metric contract.

    Every dashboard KPI should eventually be
    representable using this schema.
    """

    metric_id: str

    label: str

    value: Optional[
        float | int
    ] = None

    formatted_value: Optional[str] = None

    unit: MetricUnit = MetricUnit.decimal

    comparison: MetricComparison = Field(
        default_factory=MetricComparison
    )

    sentiment: MetricSentiment = (
        MetricSentiment.unknown
    )

    definition: Optional[str] = None

    formula: Optional[str] = None

    data_quality: MetricQuality = (
        MetricQuality.verified
    )

    source: MetricSource = Field(
        default_factory=MetricSource
    )

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


# ============================================================
# KPI GROUP
# ============================================================


class MetricGroup(BaseModel):
    """
    Group of metrics rendered together.

    Example:
        business_health
        marketing
        logistics
    """

    group_id: str

    label: str

    metrics: list[
        MetricContract
    ] = Field(
        default_factory=list
    )

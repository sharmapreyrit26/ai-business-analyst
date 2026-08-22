from typing import Any, Optional

from pydantic import BaseModel, Field

from backend.app.metric_contracts import (
    MetricContract,
    MetricQuality,
)


# ============================================================
# CALCULATION COMPONENT
# ============================================================


class DrilldownComponent(BaseModel):
    component_id: str

    label: str

    value: Optional[
        float | int
    ] = None

    formatted_value: Optional[str] = None

    operator: Optional[str] = None

    contribution_to_change: Optional[
        float
    ] = None

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


# ============================================================
# SOURCE REFERENCE
# ============================================================


class DrilldownSource(BaseModel):
    source_type: str

    source_name: str

    fields: list[str] = Field(
        default_factory=list
    )

    description: Optional[str] = None


# ============================================================
# DRILLDOWN RESPONSE
# ============================================================


class MetricDrilldown(BaseModel):
    metric: MetricContract

    calculation_components: list[
        DrilldownComponent
    ] = Field(
        default_factory=list
    )

    sources: list[
        DrilldownSource
    ] = Field(
        default_factory=list
    )

    limitations: list[str] = Field(
        default_factory=list
    )

    data_quality: MetricQuality = (
        MetricQuality.verified
    )

    related_metrics: list[str] = Field(
        default_factory=list
    )

    suggested_questions: list[str] = Field(
        default_factory=list
    )

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )

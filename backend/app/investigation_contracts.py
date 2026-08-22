from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# ENUMS
# ============================================================


class InvestigationSeverity(
    str,
    Enum,
):
    critical = "critical"
    warning = "warning"
    info = "info"


class InvestigationStatus(
    str,
    Enum,
):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"
    dismissed = "dismissed"


class InvestigationConfidence(
    str,
    Enum,
):
    high = "high"
    medium = "medium"
    low = "low"


# ============================================================
# DRIVER
# ============================================================


class InvestigationDriver(BaseModel):
    driver_id: str

    label: str

    metric_id: Optional[str] = None

    impact: Optional[float] = None

    contribution_percent: Optional[
        float
    ] = None

    evidence: list[str] = Field(
        default_factory=list
    )


# ============================================================
# ACTION
# ============================================================


class InvestigationAction(BaseModel):
    action_id: str

    label: str

    priority: int = 1

    status: str = "open"

    related_page: Optional[
        str
    ] = None

    metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )


# ============================================================
# EVIDENCE
# ============================================================


class InvestigationEvidence(BaseModel):
    evidence_id: str

    label: str

    value: Optional[
        float | int | str
    ] = None

    formatted_value: Optional[
        str
    ] = None

    metric_id: Optional[
        str
    ] = None

    source_engine: Optional[
        str
    ] = None

    description: Optional[
        str
    ] = None


# ============================================================
# INVESTIGATION
# ============================================================


class Investigation(BaseModel):
    investigation_id: str

    title: str

    category: str

    severity: InvestigationSeverity

    status: InvestigationStatus = (
        InvestigationStatus.open
    )

    confidence: InvestigationConfidence

    month: str

    summary: str

    estimated_impact: Optional[
        float
    ] = None

    formatted_impact: Optional[
        str
    ] = None

    primary_metric_id: Optional[
        str
    ] = None

    drivers: list[
        InvestigationDriver
    ] = Field(
        default_factory=list
    )

    evidence: list[
        InvestigationEvidence
    ] = Field(
        default_factory=list
    )

    recommended_actions: list[
        InvestigationAction
    ] = Field(
        default_factory=list
    )

    related_metrics: list[
        str
    ] = Field(
        default_factory=list
    )

    related_pages: list[
        str
    ] = Field(
        default_factory=list
    )

    scenario_suggestions: list[
        str
    ] = Field(
        default_factory=list
    )

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )

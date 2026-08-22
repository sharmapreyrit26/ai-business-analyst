from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class DataQualitySeverity(
    str,
    Enum,
):
    critical = "critical"
    warning = "warning"
    info = "info"


class DataQualityDimension(
    str,
    Enum,
):
    completeness = "completeness"
    consistency = "consistency"
    integrity = "integrity"
    freshness = "freshness"
    reconciliation = "reconciliation"


class DataQualityIssue(BaseModel):
    issue_id: str
    title: str
    severity: DataQualitySeverity
    dimension: DataQualityDimension

    dataset: Optional[str] = None
    field: Optional[str] = None

    affected_rows: int = 0
    affected_percent: Optional[float] = None

    description: Optional[str] = None

    metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )


class DataQualityScore(BaseModel):
    completeness_percent: float = 100.0
    consistency_percent: float = 100.0
    integrity_percent: float = 100.0
    freshness_percent: float = 100.0

    overall_score: float = 100.0


class ReconciliationCheck(BaseModel):
    reconciliation_id: str
    label: str

    left_label: str
    left_value: float

    right_label: str
    right_value: float

    difference: float

    tolerance: float = 0.0

    reconciled: bool

    metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )


class DataQualityReport(BaseModel):
    status: str

    score: DataQualityScore

    issues: list[
        DataQualityIssue
    ] = Field(
        default_factory=list
    )

    reconciliations: list[
        ReconciliationCheck
    ] = Field(
        default_factory=list
    )

    critical_issue_count: int = 0
    warning_count: int = 0

    suitable_for_analysis: bool = True

    limitations: list[str] = Field(
        default_factory=list
    )

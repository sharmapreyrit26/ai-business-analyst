from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# ENUMS
# ============================================================


class AlertOperator(
    str,
    Enum,
):
    greater_than = "greater_than"
    greater_than_or_equal = "greater_than_or_equal"
    less_than = "less_than"
    less_than_or_equal = "less_than_or_equal"
    equal = "equal"


class AlertSeverity(
    str,
    Enum,
):
    critical = "critical"
    warning = "warning"
    info = "info"


class AlertStatus(
    str,
    Enum,
):
    active = "active"
    triggered = "triggered"
    disabled = "disabled"


# ============================================================
# ALERT RULE
# ============================================================


class AlertRule(BaseModel):
    alert_rule_id: str

    name: str

    metric_id: str

    operator: AlertOperator

    threshold: float

    severity: AlertSeverity

    enabled: bool = True

    page: Optional[str] = None

    description: Optional[str] = None

    metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )


# ============================================================
# ALERT RESULT
# ============================================================


class AlertResult(BaseModel):
    alert_rule_id: str

    name: str

    metric_id: str

    triggered: bool

    severity: AlertSeverity

    status: AlertStatus

    current_value: Optional[float] = None

    threshold: float

    operator: AlertOperator

    message: str

    page: Optional[str] = None

    metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )

from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# INPUT CONTROLS
# ============================================================


class ScenarioChanges(BaseModel):
    """
    Structured Scenario Lab controls.

    Percent fields represent relative changes unless
    otherwise stated.

    Examples:
        orders_change_percent = 10
            -> orders increase by 10%

        marketing_spend_change_percent = -10
            -> marketing spend decreases by 10%

        rto_reduction_percent = 20
            -> RTO volume/rate reduced by 20%
    """

    orders_change_percent: float = 0.0

    aov_change_percent: float = 0.0

    rto_reduction_percent: float = 0.0

    marketing_spend_change_percent: float = 0.0

    cac_change_percent: float = 0.0

    # Reserved for the later pricing / discount model.
    # Do not calculate financial impact until a deterministic
    # discount engine exists.
    discount_rate_change_percent: float = 0.0


# ============================================================
# REQUEST
# ============================================================


class ScenarioV2Request(BaseModel):
    month: str

    changes: ScenarioChanges

    name: Optional[str] = None


# ============================================================
# CAPABILITY
# ============================================================


class ScenarioControlCapability(BaseModel):
    control_id: str

    label: str

    unit: str

    enabled: bool

    combined_supported: bool

    minimum: Optional[float] = None

    maximum: Optional[float] = None

    step: Optional[float] = None

    description: Optional[str] = None

    limitation: Optional[str] = None


# ============================================================
# WATERFALL
# ============================================================


class ScenarioWaterfallItem(BaseModel):
    driver_id: str

    label: str

    impact: Optional[float] = None

    formatted_impact: Optional[str] = None

    direction: str = "neutral"


# ============================================================
# EXPLANATION
# ============================================================


class ScenarioExplanation(BaseModel):
    headline: str

    explanation: str

    evidence: list[str] = Field(
        default_factory=list
    )


# ============================================================
# RESPONSE
# ============================================================


class ScenarioV2Response(BaseModel):
    status: str

    month: str

    name: Optional[str] = None

    scenario_type: str

    changes: ScenarioChanges

    current: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )

    projected: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )

    difference: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )

    waterfall: list[
        ScenarioWaterfallItem
    ] = Field(
        default_factory=list
    )

    explanations: list[
        ScenarioExplanation
    ] = Field(
        default_factory=list
    )

    assumptions: list[str] = Field(
        default_factory=list
    )

    limitations: list[str] = Field(
        default_factory=list
    )

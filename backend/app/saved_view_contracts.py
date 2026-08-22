from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from backend.app.analytics_context import (
    AnalyticsContext,
)


# ============================================================
# ENUMS
# ============================================================


class SavedViewScope(
    str,
    Enum,
):
    private = "private"
    workspace = "workspace"


# ============================================================
# SAVED VIEW
# ============================================================


class SavedView(BaseModel):
    saved_view_id: str

    name: str

    page: str

    context: AnalyticsContext

    scope: SavedViewScope = (
        SavedViewScope.private
    )

    description: Optional[
        str
    ] = None

    is_default: bool = False

    created_by: Optional[
        str
    ] = None

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


# ============================================================
# CREATE REQUEST
# ============================================================


class CreateSavedViewRequest(
    BaseModel
):
    name: str

    page: str

    context: AnalyticsContext

    scope: SavedViewScope = (
        SavedViewScope.private
    )

    description: Optional[
        str
    ] = None

    is_default: bool = False

    created_by: Optional[
        str
    ] = None

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )

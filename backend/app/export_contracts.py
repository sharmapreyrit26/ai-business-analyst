from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from backend.app.analytics_context import (
    AnalyticsContext,
)


# ============================================================
# ENUMS
# ============================================================


class ExportFormat(
    str,
    Enum,
):
    csv = "csv"
    json = "json"
    xlsx = "xlsx"
    pdf = "pdf"


class ExportDelivery(
    str,
    Enum,
):
    download = "download"
    email = "email"


class ExportStatus(
    str,
    Enum,
):
    ready = "ready"
    pending = "pending"
    unsupported = "unsupported"


# ============================================================
# REQUEST
# ============================================================


class ExportRequest(BaseModel):
    report_id: str

    month: Optional[str] = None

    analytics_context: Optional[
        AnalyticsContext
    ] = None

    format: ExportFormat = (
        ExportFormat.csv
    )

    delivery: ExportDelivery = (
        ExportDelivery.download
    )

    email: Optional[str] = None

    filename: Optional[str] = None

    include_metadata: bool = True


# ============================================================
# RESULT
# ============================================================


class ExportResult(BaseModel):
    export_id: str

    report_id: str

    status: ExportStatus

    format: ExportFormat

    delivery: ExportDelivery

    filename: str

    mime_type: str

    row_count: int = 0

    content: Optional[str] = None

    email: Optional[str] = None

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )

    limitations: list[str] = Field(
        default_factory=list
    )

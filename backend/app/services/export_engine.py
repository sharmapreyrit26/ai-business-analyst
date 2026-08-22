from __future__ import annotations

import csv
import json
from hashlib import sha1
from io import StringIO
from typing import Any

from backend.app.export_contracts import (
    ExportDelivery,
    ExportFormat,
    ExportRequest,
    ExportResult,
    ExportStatus,
)


# ============================================================
# MIME TYPES
# ============================================================


MIME_TYPES = {
    ExportFormat.csv:
        "text/csv",

    ExportFormat.json:
        "application/json",

    ExportFormat.xlsx:
        (
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),

    ExportFormat.pdf:
        "application/pdf",
}


# ============================================================
# HELPERS
# ============================================================


def _export_id(
    request: ExportRequest,
) -> str:
    raw = (
        f"{request.report_id}|"
        f"{request.month}|"
        f"{request.format}|"
        f"{request.delivery}|"
        f"{request.email}"
    )

    digest = (
        sha1(
            raw.encode(
                "utf-8"
            )
        )
        .hexdigest()[:12]
        .upper()
    )

    return (
        f"EXP_{digest}"
    )


def _safe_filename(
    request: ExportRequest,
) -> str:
    if request.filename:
        base = (
            request.filename
            .strip()
            .replace(
                " ",
                "_",
            )
        )

    else:
        parts = [
            "profitlens",
            request.report_id,
        ]

        if request.month:
            parts.append(
                request.month
            )

        base = "_".join(
            parts
        )

    extension = (
        request.format.value
    )

    if base.lower().endswith(
        f".{extension}"
    ):
        return base

    return (
        f"{base}.{extension}"
    )


def _validate_request(
    request: ExportRequest,
):
    if (
        request.delivery
        == ExportDelivery.email
        and not request.email
    ):
        raise ValueError(
            "Email delivery requires "
            "an email address."
        )

    if (
        request.format
        in {
            ExportFormat.xlsx,
            ExportFormat.pdf,
        }
    ):
        return


def _normalize_rows(
    data: Any,
) -> list[dict]:
    """
    Convert supported report payloads into rows.

    Supported:
    - list[dict]
    - dict with a `data` list
    - flat dict
    """

    if isinstance(
        data,
        list,
    ):
        if all(
            isinstance(
                row,
                dict,
            )
            for row in data
        ):
            return data

        raise ValueError(
            "List exports require dictionary rows."
        )

    if isinstance(
        data,
        dict,
    ):
        nested_data = (
            data.get(
                "data"
            )
        )

        if (
            isinstance(
                nested_data,
                list,
            )
            and all(
                isinstance(
                    row,
                    dict,
                )
                for row in nested_data
            )
        ):
            return nested_data

        return [
            data
        ]

    raise ValueError(
        "Unsupported export payload."
    )


def _stringify_value(
    value,
):
    if value is None:
        return ""

    if isinstance(
        value,
        (
            dict,
            list,
            tuple,
        ),
    ):
        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )

    return value


# ============================================================
# CSV
# ============================================================


def _build_csv(
    rows: list[dict],
) -> str:
    if not rows:
        return ""

    fieldnames = []

    seen = set()

    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(
                    key
                )
                fieldnames.append(
                    key
                )

    buffer = StringIO()

    writer = csv.DictWriter(
        buffer,
        fieldnames=fieldnames,
        extrasaction="ignore",
    )

    writer.writeheader()

    for row in rows:
        writer.writerow(
            {
                key:
                    _stringify_value(
                        row.get(
                            key
                        )
                    )
                for key
                in fieldnames
            }
        )

    return buffer.getvalue()


# ============================================================
# JSON
# ============================================================


def _build_json(
    data: Any,
) -> str:
    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
        default=str,
        allow_nan=False,
    )


# ============================================================
# MAIN EXPORT BUILDER
# ============================================================


def build_export(
    request: ExportRequest,
    *,
    data: Any,
    metadata: dict | None = None,
) -> ExportResult:
    """
    Build a reusable ProfitLens export artifact.

    This service does not fetch analytics itself.

    Analytics engines remain responsible for financial
    truth. Export logic only serializes their output.
    """

    _validate_request(
        request
    )

    rows = (
        _normalize_rows(
            data
        )
    )

    export_id = (
        _export_id(
            request
        )
    )

    filename = (
        _safe_filename(
            request
        )
    )

    common_metadata = {
        "month":
            request.month,

        "include_metadata":
            request.include_metadata,

        **(
            metadata
            or {}
        ),
    }

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    if (
        request.format
        == ExportFormat.csv
    ):
        content = (
            _build_csv(
                rows
            )
        )

        return ExportResult(
            export_id=export_id,
            report_id=(
                request.report_id
            ),
            status=(
                ExportStatus.ready
            ),
            format=request.format,
            delivery=(
                request.delivery
            ),
            filename=filename,
            mime_type=(
                MIME_TYPES[
                    request.format
                ]
            ),
            row_count=len(
                rows
            ),
            content=content,
            email=request.email,
            metadata=(
                common_metadata
            ),
        )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    if (
        request.format
        == ExportFormat.json
    ):
        content = (
            _build_json(
                data
            )
        )

        return ExportResult(
            export_id=export_id,
            report_id=(
                request.report_id
            ),
            status=(
                ExportStatus.ready
            ),
            format=request.format,
            delivery=(
                request.delivery
            ),
            filename=filename,
            mime_type=(
                MIME_TYPES[
                    request.format
                ]
            ),
            row_count=len(
                rows
            ),
            content=content,
            email=request.email,
            metadata=(
                common_metadata
            ),
        )

    # --------------------------------------------------------
    # XLSX / PDF
    # --------------------------------------------------------

    return ExportResult(
        export_id=export_id,
        report_id=(
            request.report_id
        ),
        status=(
            ExportStatus.pending
        ),
        format=request.format,
        delivery=(
            request.delivery
        ),
        filename=filename,
        mime_type=(
            MIME_TYPES[
                request.format
            ]
        ),
        row_count=len(
            rows
        ),
        content=None,
        email=request.email,
        metadata=(
            common_metadata
        ),
        limitations=[
            (
                f"{request.format.value.upper()} "
                "binary generation is handled "
                "by the asynchronous report renderer."
            )
        ],
    )


# ============================================================
# EMAIL DELIVERY CONTRACT
# ============================================================


def build_email_delivery_payload(
    export: ExportResult,
) -> dict:
    """
    Convert an export into the payload expected by a
    future email-delivery worker.

    No email is sent from the analytics engine itself.
    """

    if (
        export.delivery
        != ExportDelivery.email
    ):
        raise ValueError(
            "Export is not configured "
            "for email delivery."
        )

    if not export.email:
        raise ValueError(
            "Email address is missing."
        )

    return {
        "export_id":
            export.export_id,

        "recipient":
            export.email,

        "subject":
            (
                "Your ProfitLens "
                f"{export.report_id} report"
            ),

        "filename":
            export.filename,

        "mime_type":
            export.mime_type,

        "content":
            export.content,

        "metadata":
            export.metadata,
    }

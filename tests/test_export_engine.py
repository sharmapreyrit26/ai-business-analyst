import json

import pytest

from backend.app.export_contracts import (
    ExportDelivery,
    ExportFormat,
    ExportRequest,
    ExportStatus,
)

from backend.app.services.export_engine import (
    build_email_delivery_payload,
    build_export,
)


def test_csv_export():
    request = ExportRequest(
        report_id="marketing",
        month="2025-11",
        format=ExportFormat.csv,
    )

    result = build_export(
        request,
        data=[
            {
                "channel": "Meta",
                "spend": 1000,
                "roas": 4.2,
            },
            {
                "channel": "Google",
                "spend": 800,
                "roas": 3.8,
            },
        ],
    )

    assert (
        result.status
        == ExportStatus.ready
    )

    assert (
        result.filename
        == (
            "profitlens_marketing_"
            "2025-11.csv"
        )
    )

    assert (
        result.row_count
        == 2
    )

    assert (
        "Meta"
        in result.content
    )

    assert (
        "Google"
        in result.content
    )


def test_csv_handles_nested_values():
    import csv
    import io

    request = ExportRequest(
        report_id="overview",
        format=ExportFormat.csv,
    )

    result = build_export(
        request,
        data={
            "month": "2025-11",
            "metrics": {
                "revenue": 100,
                "orders": 10,
            },
        },
    )

    assert (
        result.row_count
        == 1
    )

    reader = csv.DictReader(
        io.StringIO(
            result.content
        )
    )

    rows = list(
        reader
    )

    assert len(
        rows
    ) == 1

    assert (
        rows[0]["month"]
        == "2025-11"
    )

    nested = json.loads(
        rows[0]["metrics"]
    )

    assert (
        nested["revenue"]
        == 100
    )

    assert (
        nested["orders"]
        == 10
    )


def test_json_export():
    request = ExportRequest(
        report_id="logistics",
        month="2025-11",
        format=ExportFormat.json,
    )

    result = build_export(
        request,
        data={
            "rto_rate_percent":
                12.02,
            "ndr_rate_percent":
                19.05,
        },
    )

    parsed = json.loads(
        result.content
    )

    assert (
        parsed[
            "rto_rate_percent"
        ]
        == 12.02
    )


def test_email_requires_recipient():
    request = ExportRequest(
        report_id="marketing",
        delivery=(
            ExportDelivery.email
        ),
    )

    with pytest.raises(
        ValueError
    ):
        build_export(
            request,
            data=[],
        )


def test_email_payload():
    request = ExportRequest(
        report_id="marketing",
        month="2025-11",
        format=ExportFormat.csv,
        delivery=(
            ExportDelivery.email
        ),
        email=(
            "founder@example.com"
        ),
    )

    export = build_export(
        request,
        data=[
            {
                "channel": "Meta",
                "roas": 5.2,
            }
        ],
    )

    payload = (
        build_email_delivery_payload(
            export
        )
    )

    assert (
        payload["recipient"]
        == "founder@example.com"
    )

    assert (
        payload["filename"]
        == (
            "profitlens_marketing_"
            "2025-11.csv"
        )
    )


def test_pdf_export_is_pending_renderer():
    request = ExportRequest(
        report_id=(
            "business_health"
        ),
        month="2025-11",
        format=ExportFormat.pdf,
    )

    result = build_export(
        request,
        data={
            "revenue":
                11010422,
        },
    )

    assert (
        result.status
        == ExportStatus.pending
    )

    assert (
        result.content
        is None
    )

    assert len(
        result.limitations
    ) == 1


def test_xlsx_export_is_pending_renderer():
    request = ExportRequest(
        report_id="inventory",
        format=ExportFormat.xlsx,
    )

    result = build_export(
        request,
        data=[
            {
                "sku": "SKU_1",
                "stock": 100,
            }
        ],
    )

    assert (
        result.status
        == ExportStatus.pending
    )


def test_custom_filename():
    request = ExportRequest(
        report_id="marketing",
        format=ExportFormat.csv,
        filename=(
            "November Marketing"
        ),
    )

    result = build_export(
        request,
        data=[],
    )

    assert (
        result.filename
        == "November_Marketing.csv"
    )


def test_export_id_is_stable():
    request = ExportRequest(
        report_id="marketing",
        month="2025-11",
        format=ExportFormat.csv,
    )

    first = build_export(
        request,
        data=[],
    )

    second = build_export(
        request,
        data=[],
    )

    assert (
        first.export_id
        == second.export_id
    )

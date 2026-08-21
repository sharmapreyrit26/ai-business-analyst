from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


# ============================================================
# LOGISTICS SUMMARY
# ============================================================


def test_logistics_summary_endpoint():
    response = client.get(
        "/analytics/d2c/logistics/2025-11"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["month"] == "2025-11"
    assert "summary" in payload
    assert "definitions" in payload

    summary = payload["summary"]

    assert summary["total_orders"] == 9501
    assert summary["delivered_orders"] == 8246

    assert (
        summary["delivery_rate_percent"]
        == 86.79
    )

    assert summary["rto_orders"] == 1142

    assert (
        summary["rto_rate_percent"]
        == 12.02
    )

    assert summary["returned_orders"] == 588

    assert (
        summary["return_rate_percent"]
        == 6.19
    )

    assert summary["ndr_orders"] == 1810

    assert (
        summary["ndr_rate_percent"]
        == 19.05
    )

    assert summary["cod_orders"] == 4961

    assert (
        summary["cod_share_percent"]
        == 52.22
    )

    assert (
        summary["average_delivery_tat_days"]
        == 5.89
    )

    assert (
        summary["median_delivery_tat_days"]
        == 6.0
    )

    assert (
        summary["p90_delivery_tat_days"]
        == 8.0
    )

    assert (
        summary["on_time_delivery_percent"]
        == 43.02
    )

    assert (
        summary["late_delivery_percent"]
        == 56.98
    )


def test_logistics_invalid_month_returns_404():
    response = client.get(
        "/analytics/d2c/logistics/2099-01"
    )

    assert response.status_code == 404


# ============================================================
# COURIER PERFORMANCE
# ============================================================


def test_courier_performance_endpoint():
    response = client.get(
        "/analytics/d2c/couriers/2025-11"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["month"] == "2025-11"

    rows = payload["data"]

    assert len(rows) == 6

    courier_names = {
        row["courier_name"]
        for row in rows
    }

    assert courier_names == {
        "Blue Dart",
        "Delhivery",
        "DTDC",
        "Ecom Express",
        "Xpressbees",
        "Unknown",
    }


def test_blue_dart_is_fastest_known_courier():
    response = client.get(
        "/analytics/d2c/couriers/2025-11"
    )

    rows = response.json()["data"]

    known = [
        row
        for row in rows
        if row["courier_name"] != "Unknown"
    ]

    fastest = min(
        known,
        key=lambda row:
            row["average_delivery_tat_days"]
    )

    assert (
        fastest["courier_name"]
        == "Blue Dart"
    )

    assert (
        fastest["average_delivery_tat_days"]
        == 4.44
    )


# ============================================================
# COD VS PREPAID
# ============================================================


def test_payment_logistics_endpoint():
    response = client.get(
        "/analytics/d2c/payment-logistics/2025-11"
    )

    assert response.status_code == 200

    payload = response.json()

    rows = payload["data"]

    assert len(rows) == 2

    groups = {
        row["payment_group"]
        for row in rows
    }

    assert groups == {
        "COD",
        "Prepaid",
    }


def test_cod_has_higher_rto_than_prepaid():
    response = client.get(
        "/analytics/d2c/payment-logistics/2025-11"
    )

    rows = response.json()["data"]

    cod = next(
        row
        for row in rows
        if row["payment_group"] == "COD"
    )

    prepaid = next(
        row
        for row in rows
        if row["payment_group"] == "Prepaid"
    )

    assert cod["rto_rate_percent"] == 19.35
    assert prepaid["rto_rate_percent"] == 4.01

    assert (
        cod["rto_rate_percent"]
        > prepaid["rto_rate_percent"]
    )

    assert cod["ndr_rate_percent"] == 27.35
    assert prepaid["ndr_rate_percent"] == 9.98


# ============================================================
# ZONE PERFORMANCE
# ============================================================


def test_zone_performance_endpoint():
    response = client.get(
        "/analytics/d2c/zones/2025-11"
    )

    assert response.status_code == 200

    payload = response.json()

    rows = payload["data"]

    assert len(rows) == 5

    zones = {
        row["zone"]
        for row in rows
    }

    assert zones == {
        "North",
        "South",
        "East",
        "West",
        "Central",
    }


def test_zone_orders_reconcile_to_total_orders():
    response = client.get(
        "/analytics/d2c/zones/2025-11"
    )

    rows = response.json()["data"]

    total = sum(
        row["orders"]
        for row in rows
    )

    assert total == 9501
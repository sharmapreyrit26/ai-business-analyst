from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


# ============================================================
# CUSTOMER SUMMARY
# ============================================================


def test_customer_summary_endpoint():
    response = client.get(
        "/analytics/d2c/customers/2025-11"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["month"] == "2025-11"

    assert data["active_customers"] == 8974
    assert data["new_customers"] == 3229
    assert data["repeat_customers"] == 5745

    assert (
        data["repeat_customer_rate_percent"]
        == 64.02
    )

    assert data["orders"] == 9501

    assert (
        data["orders_per_customer"]
        == 1.06
    )

    assert data["rto_orders"] == 1142

    assert (
        data["rto_rate_percent"]
        == 12.02
    )

    assert data["returned_orders"] == 588

    assert (
        data["return_rate_percent"]
        == 6.19
    )

    assert data["cod_orders"] == 4961

    assert (
        data["cod_share_percent"]
        == 52.22
    )


# ============================================================
# INVALID CUSTOMER MONTH
# ============================================================


def test_customer_summary_invalid_month():
    response = client.get(
        "/analytics/d2c/customers/2099-01"
    )

    assert response.status_code == 404


# ============================================================
# ACQUISITION CHANNELS
# ============================================================


def test_acquisition_channels_endpoint():
    response = client.get(
        "/analytics/d2c/"
        "acquisition-channels/2025-11"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["month"] == "2025-11"

    assert (
        payload["metric_basis"]
        == "placed_order_value"
    )

    rows = payload["data"]

    assert len(rows) == 6

    channels = {
        row["acquisition_channel"]
        for row in rows
    }

    assert channels == {
        "Meta",
        "Google",
        "Organic",
        "Influencer",
        "Affiliate",
        "Unknown",
    }


def test_acquisition_channel_totals_reconcile():
    response = client.get(
        "/analytics/d2c/"
        "acquisition-channels/2025-11"
    )

    assert response.status_code == 200

    rows = response.json()["data"]

    total_customers = sum(
        row["customers"]
        for row in rows
    )

    total_orders = sum(
        row["orders"]
        for row in rows
    )

    assert total_customers == 8974
    assert total_orders == 9501


def test_acquisition_channels_invalid_month():
    response = client.get(
        "/analytics/d2c/"
        "acquisition-channels/2099-01"
    )

    assert response.status_code == 404


# ============================================================
# CUSTOMER COHORTS
# ============================================================


def test_customer_cohorts_endpoint():
    response = client.get(
        "/analytics/d2c/customer-cohorts"
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["retention_type"]
        == "observed_historical"
    )

    assert payload["predictive"] is False

    rows = payload["data"]

    assert len(rows) == 78


def test_january_customer_cohort():
    response = client.get(
        "/analytics/d2c/customer-cohorts"
    )

    rows = response.json()["data"]

    january_zero = next(
        row
        for row in rows
        if (
            row["cohort_month"]
            == "2025-01"
            and
            row[
                "months_since_first_order"
            ]
            == 0
        )
    )

    assert january_zero["cohort_size"] == 5187

    assert (
        january_zero["active_customers"]
        == 5187
    )

    assert (
        january_zero["retention_percent"]
        == 100.0
    )


def test_customer_cohort_retention_bounds():
    response = client.get(
        "/analytics/d2c/customer-cohorts"
    )

    rows = response.json()["data"]

    for row in rows:
        assert (
            0
            <= row["retention_percent"]
            <= 100
        )

        assert (
            row["active_customers"]
            <= row["cohort_size"]
        )
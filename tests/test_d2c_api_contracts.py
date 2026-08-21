import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


# ============================================================
# DATASET SUMMARY
# ============================================================


def test_d2c_dataset_summary_endpoint():
    response = client.get(
        "/analytics/d2c/dataset-summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["dataset"]
        == "ProfitLens India D2C Demo Dataset v1.1"
    )

    assert data["orders"] == 100000
    assert data["order_items"] == 173969
    assert data["customers"] == 58000
    assert data["products"] == 250
    assert data["payments"] == 100000
    assert data["marketing_rows"] == 2222
    assert data["couriers"] == 5
    assert data["inventory_rows"] == 750

    assert data["start_date"] == "2025-01-10"
    assert data["end_date"] == "2025-12-18"


# ============================================================
# REPORTING PERIODS
# ============================================================


def test_d2c_reporting_periods_endpoint():
    response = client.get(
        "/analytics/d2c/reporting-periods"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(
        data["months"]
    ) == 12

    assert (
        data["default_month"]
        == "2025-11"
    )

    assert "2025-01" in (
        data["partial_months"]
    )

    assert "2025-12" in (
        data["partial_months"]
    )

    assert "2025-11" in (
        data["complete_months"]
    )

    assert "2025-10" in (
        data["complete_months"]
    )

    assert "2025-01" not in (
        data["complete_months"]
    )

    assert "2025-12" not in (
        data["complete_months"]
    )


# ============================================================
# FINANCIALS
# ============================================================


def test_d2c_financials_endpoint():
    response = client.get(
        "/analytics/d2c/financials/2025-11"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["month"] == "2025-11"
    assert data["orders"] == 9501

    assert (
        data["realized_revenue"]
        == 11010422.0
    )

    assert (
        data[
            "contribution_profit_before_marketing"
        ]
        == 3627101.68
    )

    assert (
        data[
            "contribution_margin_percent"
        ]
        == 32.94
    )

    assert (
        data["previous_month"]
        == "2025-10"
    )


# ============================================================
# PROFITABILITY
# ============================================================


def test_d2c_profitability_endpoint():
    response = client.get(
        "/analytics/d2c/profitability/2025-11"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["month"] == "2025-11"
    assert data["orders"] == 9501

    assert (
        data["realized_revenue"]
        == 11010422.0
    )

    assert (
        data[
            "contribution_profit_after_marketing"
        ]
        == 2282453.47
    )

    assert (
        data[
            "contribution_margin_after_marketing_percent"
        ]
        == 20.73
    )

    assert data["roas"] == 5.32
    assert data["cac"] == 416.43

    assert (
        data[
            "marketing_attribution_level"
        ]
        == "aggregate_monthly"
    )

    assert (
        data[
            "order_level_marketing_allocation_available"
        ]
        is False
    )


# ============================================================
# INVALID MONTH
# ============================================================


def test_d2c_financials_invalid_month_returns_404():
    response = client.get(
        "/analytics/d2c/financials/2099-01"
    )

    assert response.status_code == 404


def test_d2c_profitability_invalid_month_returns_404():
    response = client.get(
        "/analytics/d2c/profitability/2099-01"
    )

    assert response.status_code == 404


# ============================================================
# MONTHLY HISTORY
# ============================================================


def test_d2c_monthly_financials_endpoint():
    response = client.get(
        "/analytics/d2c/monthly-financials"
    )

    assert response.status_code == 200

    data = response.json()

    assert "data" in data

    rows = data["data"]

    assert len(rows) == 12

    months = [
        row["month"]
        for row in rows
    ]

    assert "2025-01" in months
    assert "2025-10" in months
    assert "2025-11" in months
    assert "2025-12" in months


def test_d2c_monthly_profitability_endpoint():
    response = client.get(
        "/analytics/d2c/monthly-profitability"
    )

    assert response.status_code == 200

    data = response.json()

    assert "data" in data

    rows = data["data"]

    assert len(rows) == 12

    november = next(
        row
        for row in rows
        if row["month"]
        == "2025-11"
    )

    assert (
        november[
            "contribution_profit_after_marketing"
        ]
        == 2282453.47
    )

    assert november["roas"] == pytest.approx(
    5.32,
    abs=0.01,
)
def test_d2c_products_endpoint():
    response = client.get(
        "/analytics/d2c/products/2025-11"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["month"] == "2025-11"
    assert "summary" in data
    assert "products" in data

    summary = data["summary"]

    assert summary["total_products"] == 250
    assert summary["total_net_revenue"] == 13453530.0
    assert summary["total_gross_profit"] == 6130868.63
    assert summary["gross_margin_percent"] == 45.57
    assert summary["loss_making_products"] == 5

    assert (
        summary["sku_contribution_profit_available"]
        is False
    )

    assert len(data["products"]) == 250


def test_d2c_products_invalid_month_returns_404():
    response = client.get(
        "/analytics/d2c/products/2099-01"
    )

    assert response.status_code == 404


def test_d2c_categories_endpoint():
    response = client.get(
        "/analytics/d2c/categories/2025-11"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["month"] == "2025-11"
    assert "categories" in data

    categories = data["categories"]

    assert len(categories) == 8

    ethnic_wear = next(
        row
        for row in categories
        if row["category"] == "Ethnic Wear"
    )

    assert ethnic_wear["products"] == 28
    assert ethnic_wear["orders"] == 1803
    assert ethnic_wear["net_revenue"] == 2587795.0
    assert ethnic_wear["gross_profit"] == 1224512.35
    assert ethnic_wear["gross_margin_percent"] == 47.32
    assert ethnic_wear["rto_orders"] == 218
    assert ethnic_wear["returned_orders"] == 117
    assert ethnic_wear["rto_rate_percent"] == 12.09
    assert ethnic_wear["return_rate_percent"] == 6.49


def test_d2c_categories_invalid_month_returns_404():
    response = client.get(
        "/analytics/d2c/categories/2099-01"
    )

    assert response.status_code == 404
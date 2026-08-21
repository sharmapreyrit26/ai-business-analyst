import pytest

from backend.app.services.d2c_data_loader import (
    get_d2c_dataset_summary,
)

from backend.app.services.d2c_financial_engine import (
    get_d2c_financial_summary,
    get_d2c_order_financials,
    get_monthly_d2c_financials,
)

from backend.app.services.d2c_profitability_engine import (
    get_monthly_profitability,
    get_profitability_summary,
)


def test_d2c_dataset_summary():
    summary = get_d2c_dataset_summary()

    assert summary["dataset"] == (
        "ProfitLens India D2C Demo Dataset v1.1"
    )
    assert summary["orders"] == 100000
    assert summary["order_items"] == 173969
    assert summary["customers"] == 58000
    assert summary["products"] == 250
    assert summary["payments"] == 100000
    assert summary["couriers"] == 5
    assert summary["inventory_rows"] == 750
    assert summary["start_date"] == "2025-01-10"
    assert summary["end_date"] == "2025-12-18"


def test_failed_orders_do_not_recognize_revenue():
    df = get_d2c_order_financials()

    failed = df[
        df["order_status"]
        .str.lower()
        .isin(
            [
                "rto",
                "cancelled",
                "canceled",
            ]
        )
    ]

    assert (
        failed["realized_revenue"].sum()
        == pytest.approx(
            0.0,
            abs=0.01,
        )
    )


def test_rto_orders_are_loss_making():
    df = get_d2c_order_financials()

    rto = df[
        df["order_status"].str.lower()
        == "rto"
    ]

    assert (
        rto[
            "contribution_profit_before_marketing"
        ].sum()
        < 0
    )

    assert rto["rto_cost"].sum() > 0


def test_delivered_orders_generate_positive_revenue():
    df = get_d2c_order_financials()

    delivered = df[
        df["order_status"].str.lower()
        == "delivered"
    ]

    assert (
        delivered["realized_revenue"].sum()
        > 0
    )

    assert (
        delivered[
            "contribution_profit_before_marketing"
        ].sum()
        > 0
    )


def test_november_2025_financial_summary():
    result = get_d2c_financial_summary(
        "2025-11"
    )

    assert result["orders"] == 9501

    assert (
        result["realized_revenue"]
        == pytest.approx(
            11010422.0,
            abs=0.01,
        )
    )

    assert (
        result["gross_profit"]
        == pytest.approx(
            4462430.23,
            abs=0.01,
        )
    )

    assert (
        result[
            "contribution_profit_before_marketing"
        ]
        == pytest.approx(
            3627101.68,
            abs=0.01,
        )
    )

    assert (
        result[
            "contribution_margin_percent"
        ]
        == pytest.approx(
            32.94,
            abs=0.01,
        )
    )


def test_october_is_festive_revenue_peak():
    monthly = get_monthly_d2c_financials()

    highest_month = (
        monthly.sort_values(
            "realized_revenue",
            ascending=False,
        )
        .iloc[0]
    )

    assert (
        highest_month["month"]
        == "2025-10"
    )


def test_november_profitability_summary():
    result = get_profitability_summary(
        "2025-11"
    )

    assert (
        result["marketing_spend"]
        == pytest.approx(
            1344648.21,
            abs=0.01,
        )
    )

    assert (
        result["roas"]
        == pytest.approx(
            5.32,
            abs=0.01,
        )
    )

    assert (
        result["cac"]
        == pytest.approx(
            416.43,
            abs=0.01,
        )
    )

    assert (
        result[
            "contribution_profit_after_marketing"
        ]
        == pytest.approx(
            2282453.47,
            abs=0.01,
        )
    )

    assert (
        result[
            "contribution_margin_after_marketing_percent"
        ]
        == pytest.approx(
            20.73,
            abs=0.01,
        )
    )


def test_marketing_never_increases_contribution_profit():
    monthly = get_monthly_profitability()

    assert (
        monthly[
            "contribution_profit_after_marketing"
        ]
        <= monthly[
            "contribution_profit_before_marketing"
        ]
    ).all()


def test_marketing_spend_is_non_negative():
    monthly = get_monthly_profitability()

    assert (
        monthly[
            "marketing_spend"
        ]
        >= 0
    ).all()


def test_profitability_has_all_12_months():
    monthly = get_monthly_profitability()

    assert (
        len(
            monthly["month"].unique()
        )
        == 12
    )


def test_invalid_d2c_month_raises_error():
    with pytest.raises(
        ValueError
    ):
        get_profitability_summary(
            "2099-01"
        )
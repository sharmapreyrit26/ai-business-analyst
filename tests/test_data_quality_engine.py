import pandas as pd

from backend.app.data_quality_contracts import (
    DataQualityDimension,
    DataQualitySeverity,
)

from backend.app.services.data_quality_engine import (
    build_data_quality_report,
    build_reconciliation,
    calculate_quality_score,
    check_duplicate_key,
    check_foreign_key_integrity,
    check_required_fields,
)


def test_required_field_missing():
    dataframe = pd.DataFrame(
        [
            {
                "order_id": "1",
            }
        ]
    )

    issues = (
        check_required_fields(
            dataframe,
            dataset_name="orders",
            required_fields=[
                "order_id",
                "customer_id",
            ],
        )
    )

    assert len(
        issues
    ) == 1

    assert (
        issues[0].severity
        == DataQualitySeverity.critical
    )

    assert (
        issues[0].field
        == "customer_id"
    )


def test_missing_values_warning():
    dataframe = pd.DataFrame(
        [
            {
                "order_id": "1",
                "customer_id": "A",
            },
            {
                "order_id": "2",
                "customer_id": None,
            },
            {
                "order_id": "3",
                "customer_id": "C",
            },
            {
                "order_id": "4",
                "customer_id": "D",
            },
            {
                "order_id": "5",
                "customer_id": "E",
            },
            {
                "order_id": "6",
                "customer_id": "F",
            },
            {
                "order_id": "7",
                "customer_id": "G",
            },
            {
                "order_id": "8",
                "customer_id": "H",
            },
            {
                "order_id": "9",
                "customer_id": "I",
            },
            {
                "order_id": "10",
                "customer_id": "J",
            },
            {
                "order_id": "11",
                "customer_id": "K",
            },
        ]
    )

    issues = (
        check_required_fields(
            dataframe,
            dataset_name="orders",
            required_fields=[
                "customer_id"
            ],
        )
    )

    assert (
        issues[0].severity
        == DataQualitySeverity.warning
    )


def test_duplicate_key():
    dataframe = pd.DataFrame(
        [
            {
                "order_id": "1",
            },
            {
                "order_id": "1",
            },
            {
                "order_id": "2",
            },
        ]
    )

    issues = check_duplicate_key(
        dataframe,
        dataset_name="orders",
        key_field="order_id",
    )

    assert len(
        issues
    ) == 1

    assert (
        issues[0].dimension
        == DataQualityDimension.integrity
    )


def test_foreign_key_integrity():
    orders = pd.DataFrame(
        [
            {
                "order_id": "1",
            },
            {
                "order_id": "2",
            },
        ]
    )

    items = pd.DataFrame(
        [
            {
                "order_id": "1",
            },
            {
                "order_id": "999",
            },
        ]
    )

    issues = (
        check_foreign_key_integrity(
            items,
            orders,
            child_dataset=(
                "order_items"
            ),
            child_field=(
                "order_id"
            ),
            parent_dataset=(
                "orders"
            ),
            parent_field=(
                "order_id"
            ),
        )
    )

    assert len(
        issues
    ) == 1

    assert (
        issues[0].affected_rows
        == 1
    )


def test_reconciliation_passes():
    result = build_reconciliation(
        reconciliation_id=(
            "revenue"
        ),
        label=(
            "Revenue Reconciliation"
        ),
        left_label=(
            "Order Items"
        ),
        left_value=1000,
        right_label="Orders",
        right_value=1000,
        tolerance=0,
    )

    assert (
        result.reconciled
        is True
    )

    assert (
        result.difference
        == 0
    )


def test_reconciliation_fails():
    result = build_reconciliation(
        reconciliation_id=(
            "revenue"
        ),
        label=(
            "Revenue Reconciliation"
        ),
        left_label=(
            "Order Items"
        ),
        left_value=1000,
        right_label="Orders",
        right_value=900,
        tolerance=0,
    )

    assert (
        result.reconciled
        is False
    )


def test_quality_score_reduces_for_issues():
    dataframe = pd.DataFrame(
        [
            {
                "order_id": "1",
            }
        ]
    )

    issues = (
        check_required_fields(
            dataframe,
            dataset_name="orders",
            required_fields=[
                "customer_id"
            ],
        )
    )

    score = (
        calculate_quality_score(
            issues
        )
    )

    assert (
        score.overall_score
        < 100
    )


def test_clean_report_is_ready():
    report = (
        build_data_quality_report(
            issues=[],
            reconciliations=[
                build_reconciliation(
                    reconciliation_id=(
                        "revenue"
                    ),
                    label=(
                        "Revenue"
                    ),
                    left_label="A",
                    left_value=100,
                    right_label="B",
                    right_value=100,
                )
            ],
        )
    )

    assert (
        report.status
        == "ready"
    )

    assert (
        report.suitable_for_analysis
        is True
    )


def test_critical_issue_blocks_analysis():
    dataframe = pd.DataFrame(
        [
            {
                "order_id": "1",
            }
        ]
    )

    issues = (
        check_required_fields(
            dataframe,
            dataset_name="orders",
            required_fields=[
                "customer_id"
            ],
        )
    )

    report = (
        build_data_quality_report(
            issues=issues
        )
    )

    assert (
        report.status
        == "blocked"
    )

    assert (
        report.suitable_for_analysis
        is False
    )


def test_failed_reconciliation_blocks_analysis():
    reconciliation = (
        build_reconciliation(
            reconciliation_id=(
                "discount"
            ),
            label=(
                "Discount Reconciliation"
            ),
            left_label=(
                "Order Items"
            ),
            left_value=100,
            right_label="Orders",
            right_value=90,
        )
    )

    report = (
        build_data_quality_report(
            issues=[],
            reconciliations=[
                reconciliation
            ],
        )
    )

    assert (
        report.suitable_for_analysis
        is False
    )

from __future__ import annotations

from hashlib import sha1

import pandas as pd

from backend.app.data_quality_contracts import (
    DataQualityDimension,
    DataQualityIssue,
    DataQualityReport,
    DataQualityScore,
    DataQualitySeverity,
    ReconciliationCheck,
)


def _issue_id(
    title: str,
    dataset: str | None,
    field: str | None,
) -> str:
    raw = (
        f"{title}|"
        f"{dataset}|"
        f"{field}"
    )

    digest = (
        sha1(
            raw.encode("utf-8")
        )
        .hexdigest()[:12]
        .upper()
    )

    return f"DQ_{digest}"


def _safe_percent(
    numerator: int,
    denominator: int,
) -> float:
    if denominator <= 0:
        return 0.0

    return round(
        numerator
        / denominator
        * 100,
        2,
    )


def check_required_fields(
    dataframe: pd.DataFrame,
    *,
    dataset_name: str,
    required_fields: list[str],
) -> list[
    DataQualityIssue
]:
    issues = []

    total_rows = len(
        dataframe
    )

    for field in required_fields:

        if field not in dataframe.columns:
            issues.append(
                DataQualityIssue(
                    issue_id=_issue_id(
                        "Required field missing",
                        dataset_name,
                        field,
                    ),
                    title=(
                        "Required field missing"
                    ),
                    severity=(
                        DataQualitySeverity.critical
                    ),
                    dimension=(
                        DataQualityDimension.completeness
                    ),
                    dataset=dataset_name,
                    field=field,
                    affected_rows=total_rows,
                    affected_percent=(
                        100.0
                        if total_rows
                        else 0.0
                    ),
                    description=(
                        f"Required field '{field}' "
                        "is not present."
                    ),
                )
            )

            continue

        missing = (
            dataframe[field]
            .isna()
            .sum()
        )

        if missing > 0:
            percent = (
                _safe_percent(
                    int(missing),
                    total_rows,
                )
            )

            severity = (
                DataQualitySeverity.critical
                if percent >= 10
                else DataQualitySeverity.warning
            )

            issues.append(
                DataQualityIssue(
                    issue_id=_issue_id(
                        "Missing required values",
                        dataset_name,
                        field,
                    ),
                    title=(
                        "Missing required values"
                    ),
                    severity=severity,
                    dimension=(
                        DataQualityDimension.completeness
                    ),
                    dataset=dataset_name,
                    field=field,
                    affected_rows=int(
                        missing
                    ),
                    affected_percent=(
                        percent
                    ),
                    description=(
                        f"{missing} rows have "
                        f"missing values in '{field}'."
                    ),
                )
            )

    return issues


def check_duplicate_key(
    dataframe: pd.DataFrame,
    *,
    dataset_name: str,
    key_field: str,
) -> list[
    DataQualityIssue
]:
    if key_field not in dataframe.columns:
        return []

    duplicated = (
        dataframe[key_field]
        .duplicated(
            keep=False
        )
        .sum()
    )

    if duplicated <= 0:
        return []

    percent = (
        _safe_percent(
            int(duplicated),
            len(dataframe),
        )
    )

    return [
        DataQualityIssue(
            issue_id=_issue_id(
                "Duplicate key values",
                dataset_name,
                key_field,
            ),
            title=(
                "Duplicate key values"
            ),
            severity=(
                DataQualitySeverity.critical
            ),
            dimension=(
                DataQualityDimension.integrity
            ),
            dataset=dataset_name,
            field=key_field,
            affected_rows=int(
                duplicated
            ),
            affected_percent=(
                percent
            ),
            description=(
                f"{duplicated} rows contain "
                f"duplicate '{key_field}' values."
            ),
        )
    ]


def check_foreign_key_integrity(
    child: pd.DataFrame,
    parent: pd.DataFrame,
    *,
    child_dataset: str,
    child_field: str,
    parent_dataset: str,
    parent_field: str,
) -> list[
    DataQualityIssue
]:
    if (
        child_field
        not in child.columns
        or parent_field
        not in parent.columns
    ):
        return []

    parent_values = set(
        parent[parent_field]
        .dropna()
        .astype(str)
    )

    child_values = (
        child[child_field]
        .dropna()
        .astype(str)
    )

    invalid_mask = (
        ~child_values.isin(
            parent_values
        )
    )

    invalid_count = int(
        invalid_mask.sum()
    )

    if invalid_count <= 0:
        return []

    percent = (
        _safe_percent(
            invalid_count,
            len(child_values),
        )
    )

    return [
        DataQualityIssue(
            issue_id=_issue_id(
                "Broken relationship",
                child_dataset,
                child_field,
            ),
            title=(
                "Broken relationship"
            ),
            severity=(
                DataQualitySeverity.critical
            ),
            dimension=(
                DataQualityDimension.integrity
            ),
            dataset=child_dataset,
            field=child_field,
            affected_rows=(
                invalid_count
            ),
            affected_percent=(
                percent
            ),
            description=(
                f"{invalid_count} values in "
                f"{child_dataset}.{child_field} "
                "do not exist in "
                f"{parent_dataset}.{parent_field}."
            ),
        )
    ]


def build_reconciliation(
    *,
    reconciliation_id: str,
    label: str,
    left_label: str,
    left_value: float,
    right_label: str,
    right_value: float,
    tolerance: float = 0.0,
) -> ReconciliationCheck:
    difference = round(
        float(left_value)
        - float(right_value),
        2,
    )

    reconciled = (
        abs(difference)
        <= tolerance
    )

    return ReconciliationCheck(
        reconciliation_id=(
            reconciliation_id
        ),
        label=label,
        left_label=left_label,
        left_value=float(
            left_value
        ),
        right_label=(
            right_label
        ),
        right_value=float(
            right_value
        ),
        difference=difference,
        tolerance=float(
            tolerance
        ),
        reconciled=reconciled,
    )


def calculate_quality_score(
    issues: list[
        DataQualityIssue
    ],
) -> DataQualityScore:
    dimension_scores = {
        DataQualityDimension.completeness:
            100.0,
        DataQualityDimension.consistency:
            100.0,
        DataQualityDimension.integrity:
            100.0,
        DataQualityDimension.freshness:
            100.0,
    }

    penalties = {
        DataQualitySeverity.critical:
            15.0,
        DataQualitySeverity.warning:
            5.0,
        DataQualitySeverity.info:
            1.0,
    }

    for issue in issues:
        if (
            issue.dimension
            not in dimension_scores
        ):
            continue

        dimension_scores[
            issue.dimension
        ] -= penalties[
            issue.severity
        ]

    for key in dimension_scores:
        dimension_scores[key] = max(
            0.0,
            dimension_scores[key],
        )

    overall = round(
        sum(
            dimension_scores.values()
        )
        / len(
            dimension_scores
        ),
        2,
    )

    return DataQualityScore(
        completeness_percent=(
            dimension_scores[
                DataQualityDimension.completeness
            ]
        ),
        consistency_percent=(
            dimension_scores[
                DataQualityDimension.consistency
            ]
        ),
        integrity_percent=(
            dimension_scores[
                DataQualityDimension.integrity
            ]
        ),
        freshness_percent=(
            dimension_scores[
                DataQualityDimension.freshness
            ]
        ),
        overall_score=(
            overall
        ),
    )


def build_data_quality_report(
    *,
    issues: list[
        DataQualityIssue
    ],
    reconciliations: list[
        ReconciliationCheck
    ] | None = None,
    limitations: list[str] | None = None,
) -> DataQualityReport:
    reconciliations = (
        reconciliations
        or []
    )

    critical_count = sum(
        issue.severity
        == DataQualitySeverity.critical
        for issue in issues
    )

    warning_count = sum(
        issue.severity
        == DataQualitySeverity.warning
        for issue in issues
    )

    reconciliation_failures = sum(
        not item.reconciled
        for item in reconciliations
    )

    score = (
        calculate_quality_score(
            issues
        )
    )

    suitable = (
        critical_count == 0
        and reconciliation_failures == 0
    )

    if suitable:
        status = "ready"
    elif critical_count > 0:
        status = "blocked"
    else:
        status = "review"

    return DataQualityReport(
        status=status,
        score=score,
        issues=issues,
        reconciliations=(
            reconciliations
        ),
        critical_issue_count=(
            critical_count
        ),
        warning_count=(
            warning_count
        ),
        suitable_for_analysis=(
            suitable
        ),
        limitations=(
            limitations
            or []
        ),
    )

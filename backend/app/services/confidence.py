from backend.app.services.evidence import (
    build_evidence_package,
)
from backend.app.services.kpi_engine import (
    get_kpi_dashboard,
)


def _score_data_quality(data_quality: dict) -> int:
    """
    Convert data quality into a confidence component.
    """

    if not data_quality:
        return 0

    status = data_quality.get("status")

    if status == "complete":
        return 25

    if status == "healthy":
        return 25

    if status == "warning":
        return 15

    if status == "partial":
        return 8

    return 5


def _score_sample_size(kpi: dict) -> int:
    """
    Score confidence based on current-period order volume.
    """

    orders = kpi.get(
        "orders",
        {}
    ).get(
        "value",
        0
    )

    if orders >= 5000:
        return 20

    if orders >= 1000:
        return 17

    if orders >= 500:
        return 14

    if orders >= 100:
        return 10

    if orders >= 30:
        return 6

    return 2


def _score_reconciliation(
    evidence_package: dict
) -> int:
    """
    Reward deterministic driver analysis when
    revenue decomposition reconciles correctly.
    """

    revenue_evidence = evidence_package.get(
        "revenue_evidence",
        {}
    )

    reconciliation = revenue_evidence.get(
        "reconciliation",
        {}
    )

    difference = abs(
        reconciliation.get(
            "difference",
            999999
        )
    )

    if difference <= 0.01:
        return 15

    if difference <= 1:
        return 10

    if difference <= 10:
        return 5

    return 0


def _score_supporting_evidence(
    evidence_package: dict
) -> int:
    """
    Score based on number of direct evidence objects.
    """

    revenue_count = (
        evidence_package
        .get(
            "revenue_evidence",
            {}
        )
        .get(
            "evidence_count",
            0
        )
    )

    operational_count = (
        evidence_package
        .get(
            "operational_evidence",
            {}
        )
        .get(
            "evidence_count",
            0
        )
    )

    total_evidence = (
        revenue_count
        + operational_count
    )

    if total_evidence >= 8:
        return 20

    if total_evidence >= 6:
        return 17

    if total_evidence >= 4:
        return 13

    if total_evidence >= 2:
        return 8

    if total_evidence >= 1:
        return 4

    return 0


def _score_driver_strength(
    evidence_package: dict
) -> int:
    """
    Measure how clearly one driver dominates the others.
    """

    revenue_evidence = evidence_package.get(
        "revenue_evidence",
        {}
    )

    evidence = revenue_evidence.get(
        "evidence",
        []
    )

    effects = {}

    for item in evidence:

        metric = item.get("metric")

        if metric == "order_volume_effect":
            effects["order_volume"] = abs(
                item.get(
                    "value",
                    0
                )
            )

        elif metric == "aov_effect":
            effects["aov"] = abs(
                item.get(
                    "value",
                    0
                )
            )

        elif metric == "interaction_effect":
            effects["interaction"] = abs(
                item.get(
                    "value",
                    0
                )
            )

    if not effects:
        return 0

    ranked = sorted(
        effects.values(),
        reverse=True
    )

    if len(ranked) < 2:
        return 10

    largest = ranked[0]
    second = ranked[1]

    if largest == 0:
        return 0

    ratio = (
        largest / second
        if second != 0
        else 999
    )

    if ratio >= 3:
        return 20

    if ratio >= 2:
        return 17

    if ratio >= 1.5:
        return 13

    if ratio >= 1.2:
        return 9

    return 5


def _calculate_confidence_level(
    score: int
) -> str:
    """
    Convert numerical score into a confidence level.
    """

    if score >= 85:
        return "high"

    if score >= 65:
        return "medium"

    return "low"


def calculate_revenue_confidence(
    month: str
):
    """
    Calculate confidence in the measurable revenue-driver
    conclusion.

    Important:
    This confidence applies to the measured driver,
    NOT to unverified hypotheses about why the driver changed.
    """

    evidence_package = (
        build_evidence_package(
            month
        )
    )

    kpi = get_kpi_dashboard(
        month
    )

    data_quality_score = (
        _score_data_quality(
            kpi.get(
                "data_quality",
                {}
            )
        )
    )

    sample_size_score = (
        _score_sample_size(
            kpi
        )
    )

    reconciliation_score = (
        _score_reconciliation(
            evidence_package
        )
    )

    evidence_score = (
        _score_supporting_evidence(
            evidence_package
        )
    )

    driver_strength_score = (
        _score_driver_strength(
            evidence_package
        )
    )

    total_score = (
        data_quality_score
        + sample_size_score
        + reconciliation_score
        + evidence_score
        + driver_strength_score
    )

    level = (
        _calculate_confidence_level(
            total_score
        )
    )

    primary_driver = (
        evidence_package
        .get(
            "revenue_evidence",
            {}
        )
        .get(
            "primary_driver"
        )
    )

    reasons = []

    if data_quality_score >= 20:
        reasons.append(
            "Data quality for the selected period is strong."
        )
    else:
        reasons.append(
            "Data quality reduces confidence."
        )

    if sample_size_score >= 17:
        reasons.append(
            "The analysis is based on a large order sample."
        )
    elif sample_size_score <= 6:
        reasons.append(
            "The available order sample is relatively small."
        )

    if reconciliation_score == 15:
        reasons.append(
            "Revenue driver decomposition reconciles "
            "with the observed revenue change."
        )
    else:
        reasons.append(
            "Revenue decomposition has a reconciliation gap."
        )

    if driver_strength_score >= 17:
        reasons.append(
            "The primary measurable driver is substantially "
            "stronger than secondary drivers."
        )
    elif driver_strength_score <= 9:
        reasons.append(
            "Multiple drivers have similar measured impacts."
        )

    return {
        "period": month,
        "metric": "revenue",
        "confidence_score": total_score,
        "confidence_level": level,
        "primary_driver": primary_driver,
        "score_components": {
            "data_quality": data_quality_score,
            "sample_size": sample_size_score,
            "reconciliation": reconciliation_score,
            "supporting_evidence": evidence_score,
            "driver_strength": driver_strength_score,
        },
        "reasons": reasons,
        "scope": (
            "Confidence applies to the measured revenue driver. "
            "It does not establish the underlying causal reason "
            "for changes in orders, AOV, traffic, pricing, "
            "marketing, or customer behaviour."
        ),
    }


def calculate_hypothesis_confidence(
    month: str
):
    """
    Calculate confidence for each underlying business
    hypothesis separately.

    Hypotheses with missing evidence should remain low-confidence.
    """

    evidence_package = (
        build_evidence_package(
            month
        )
    )

    hypothesis_evidence = (
        evidence_package
        .get(
            "hypothesis_evidence",
            {}
        )
        .get(
            "hypotheses",
            []
        )
    )

    results = []

    for hypothesis in hypothesis_evidence:

        status = hypothesis[
            "evidence_status"
        ]

        current_evidence = hypothesis[
            "current_evidence"
        ]

        missing_evidence = hypothesis[
            "missing_evidence"
        ]

        score = 0

        if status == "supported":
            score += 70

        elif status == "partial":
            score += 35

        elif status == "insufficient":
            score += 10

        score += min(
            len(current_evidence) * 5,
            20
        )

        score -= min(
            len(missing_evidence) * 5,
            20
        )

        score = max(
            0,
            min(
                score,
                100
            )
        )

        level = (
            _calculate_confidence_level(
                score
            )
        )

        results.append({
            "hypothesis_id": hypothesis[
                "hypothesis_id"
            ],
            "hypothesis": hypothesis[
                "hypothesis"
            ],
            "confidence_score": score,
            "confidence_level": level,
            "evidence_status": status,
            "supporting_evidence": (
                current_evidence
            ),
            "missing_evidence": (
                missing_evidence
            ),
        })

    return {
        "period": month,
        "hypotheses": results,
    }


def build_confidence_report(
    month: str
):
    """
    Build the complete ProfitLens confidence report.
    """

    return {
        "period": month,

        "measured_driver_confidence": (
            calculate_revenue_confidence(
                month
            )
        ),

        "hypothesis_confidence": (
            calculate_hypothesis_confidence(
                month
            )
        ),
    }
from backend.app.investigation_contracts import (
    InvestigationSeverity,
    InvestigationStatus,
)

from backend.app.services.investigation_engine import (
    generate_investigations,
)


def test_generate_investigations():
    result = (
        generate_investigations(
            "2025-11"
        )
    )

    assert len(
        result
    ) > 0


def test_investigation_ids_are_stable_and_unique():
    first = (
        generate_investigations(
            "2025-11"
        )
    )

    second = (
        generate_investigations(
            "2025-11"
        )
    )

    first_ids = [
        item.investigation_id
        for item in first
    ]

    second_ids = [
        item.investigation_id
        for item in second
    ]

    assert (
        first_ids
        == second_ids
    )

    assert (
        len(first_ids)
        == len(
            set(first_ids)
        )
    )


def test_investigations_default_open():
    result = (
        generate_investigations(
            "2025-11"
        )
    )

    assert all(
        item.status
        == InvestigationStatus.open
        for item in result
    )


def test_revenue_investigation_exists_for_november():
    result = (
        generate_investigations(
            "2025-11"
        )
    )

    revenue = [
        item
        for item in result
        if item.category
        == "revenue"
    ]

    assert len(
        revenue
    ) >= 1

    item = revenue[0]

    assert (
        item.primary_metric_id
        == "realized_revenue"
    )

    assert len(
        item.drivers
    ) > 0

    assert len(
        item.recommended_actions
    ) > 0


def test_logistics_investigation_exists():
    result = (
        generate_investigations(
            "2025-11"
        )
    )

    logistics = [
        item
        for item in result
        if item.category
        == "logistics"
    ]

    assert len(
        logistics
    ) >= 1

    assert (
        logistics[0]
        .primary_metric_id
        == "rto_rate_percent"
    )

    assert len(
        logistics[0]
        .scenario_suggestions
    ) > 0


def test_inventory_investigation_exists():
    result = (
        generate_investigations(
            "2025-11"
        )
    )

    inventory = [
        item
        for item in result
        if item.category
        == "inventory"
    ]

    assert len(
        inventory
    ) >= 1

    item = inventory[0]

    assert (
        item.estimated_impact
        is not None
    )

    assert (
        item.estimated_impact
        > 0
    )


def test_critical_items_sort_first():
    result = (
        generate_investigations(
            "2025-11"
        )
    )

    severities = [
        item.severity
        for item in result
    ]

    if (
        InvestigationSeverity.critical
        in severities
    ):
        first_noncritical = next(
            (
                index
                for index, severity
                in enumerate(
                    severities
                )
                if severity
                != InvestigationSeverity.critical
            ),
            len(
                severities
            ),
        )

        assert all(
            severity
            == InvestigationSeverity.critical
            for severity
            in severities[
                :first_noncritical
            ]
        )


def test_investigation_serializes_cleanly():
    result = (
        generate_investigations(
            "2025-11"
        )
    )

    dumped = [
        item.model_dump(
            mode="json"
        )
        for item in result
    ]

    assert isinstance(
        dumped,
        list
    )

    assert all(
        isinstance(
            item[
                "investigation_id"
            ],
            str,
        )
        for item in dumped
    )

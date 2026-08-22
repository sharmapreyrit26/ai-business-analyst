from copy import deepcopy

from backend.app.metric_dictionary import (
    METRIC_DICTIONARY,
)

from backend.app.services.metric_builder import (
    build_metric,
)


# ============================================================
# LOOKUP
# ============================================================


def get_metric_definition(
    metric_id: str,
) -> dict:
    """
    Return one metric's canonical definition.
    """

    definition = (
        METRIC_DICTIONARY.get(
            metric_id
        )
    )

    if definition is None:
        raise ValueError(
            f"Unknown ProfitLens metric: {metric_id}"
        )

    result = deepcopy(
        definition
    )

    result[
        "metric_id"
    ] = metric_id

    return result


# ============================================================
# LIST
# ============================================================


def list_metric_definitions() -> list[dict]:
    """
    Return the complete ProfitLens metric dictionary.
    """

    result = []

    for metric_id in sorted(
        METRIC_DICTIONARY
    ):

        result.append(
            get_metric_definition(
                metric_id
            )
        )

    return result


# ============================================================
# SEARCH
# ============================================================


def search_metric_definitions(
    query: str,
) -> list[dict]:
    """
    Search metrics by:
    - metric id
    - label
    - definition
    """

    normalized_query = (
        query.strip().lower()
    )

    if not normalized_query:
        return (
            list_metric_definitions()
        )

    matches = []

    for metric_id, definition in (
        METRIC_DICTIONARY.items()
    ):

        searchable = " ".join(
            [
                metric_id,
                str(
                    definition.get(
                        "label",
                        "",
                    )
                ),
                str(
                    definition.get(
                        "definition",
                        "",
                    )
                ),
            ]
        ).lower()

        if (
            normalized_query
            in searchable
        ):
            matches.append(
                get_metric_definition(
                    metric_id
                )
            )

    return sorted(
        matches,
        key=lambda item:
            item["metric_id"],
    )


# ============================================================
# LINEAGE
# ============================================================


def get_metric_lineage(
    metric_id: str,
) -> dict:
    """
    Return only calculation and source lineage.
    """

    definition = (
        get_metric_definition(
            metric_id
        )
    )

    return {
        "metric_id":
            metric_id,

        "label":
            definition["label"],

        "formula":
            definition.get(
                "formula"
            ),

        "source_engine":
            definition.get(
                "source_engine"
            ),

        "source_tables":
            definition.get(
                "source_tables",
                [],
            ),

        "source_fields":
            definition.get(
                "source_fields",
                [],
            ),

        "grain":
            definition.get(
                "grain"
            ),

        "limitations":
            definition.get(
                "limitations",
                [],
            ),
    }


# ============================================================
# METRIC CONTRACT FROM DICTIONARY
# ============================================================


def build_registered_metric(
    metric_id: str,
    *,
    value,
    previous_value=None,
    metadata: dict | None = None,
):
    """
    Build a MetricContract using canonical
    metadata from the ProfitLens dictionary.

    This prevents individual analytics engines
    from redefining metric meaning.
    """

    definition = (
        get_metric_definition(
            metric_id
        )
    )

    return build_metric(
        metric_id=metric_id,
        label=definition[
            "label"
        ],
        value=value,
        previous_value=(
            previous_value
        ),
        unit=definition[
            "unit"
        ],
        higher_is_better=(
            definition.get(
                "higher_is_better"
            )
        ),
        definition=(
            definition.get(
                "definition"
            )
        ),
        formula=(
            definition.get(
                "formula"
            )
        ),
        data_quality=(
            definition[
                "data_quality"
            ]
        ),
        source_engine=(
            definition.get(
                "source_engine"
            )
        ),
        source_tables=(
            definition.get(
                "source_tables",
                [],
            )
        ),
        source_fields=(
            definition.get(
                "source_fields",
                [],
            )
        ),
        metadata={
            "grain":
                definition.get(
                    "grain"
                ),

            "limitations":
                definition.get(
                    "limitations",
                    [],
                ),

            **(
                metadata
                or {}
            ),
        },
    )

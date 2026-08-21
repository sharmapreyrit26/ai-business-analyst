import re


# ============================================================
# TEXT HELPERS
# ============================================================


INCREASE_TERMS = [
    "increase",
    "increases",
    "increased",
    "grow",
    "grows",
    "grew",
    "rise",
    "rises",
    "rose",
    "higher",
    "raise",
    "raises",
    "raised",
    "recover",
    "recovery",
]

DECREASE_TERMS = [
    "decrease",
    "decreases",
    "decreased",
    "decline",
    "declines",
    "declined",
    "drop",
    "drops",
    "dropped",
    "reduce",
    "reduces",
    "reduced",
    "reduction",
    "fall",
    "falls",
    "fell",
    "lower",
    "lowered",
]


def _extract_percentage(
    question: str,
):
    """
    Extract the first percentage in a question.
    """

    match = re.search(
        r"(-?\d+(?:\.\d+)?)\s*%",
        question,
    )

    if not match:
        return None

    return float(
        match.group(1)
    )


def _extract_recovery_fraction(
    question: str,
):
    """
    Understand common natural-language recovery amounts.
    """

    q = question.lower()

    if "half" in q:
        return 50.0

    if (
        "three quarters" in q
        or "three-quarters" in q
    ):
        return 75.0

    if "quarter" in q:
        return 25.0

    if (
        "all lost" in q
        or "all of the lost" in q
        or "fully recover" in q
        or "recover all" in q
    ):
        return 100.0

    return None


def _direction_from_phrase(
    phrase: str,
):
    """
    Determine direction using only the phrase
    associated with the metric being parsed.

    This prevents a later metric such as:

        RTO reduces by 20%

    from accidentally turning:

        orders increase by 10%

    into a negative order scenario.
    """

    q = phrase.lower()

    if any(
        term in q
        for term in DECREASE_TERMS
    ):
        return -1

    if any(
        term in q
        for term in INCREASE_TERMS
    ):
        return 1

    return None


def _find_metric_position(
    question: str,
    aliases: list[str],
):
    """
    Find the earliest occurrence of a metric alias.
    """

    q = question.lower()

    matches = []

    for alias in aliases:

        index = q.find(
            alias.lower()
        )

        if index >= 0:
            matches.append(
                (
                    index,
                    alias,
                )
            )

    if not matches:
        return None

    return min(
        matches,
        key=lambda item: item[0],
    )


def _extract_metric_change(
    question: str,
    aliases: list[str],
):
    """
    Extract the percentage change associated with one metric.

    Handles:

    - orders increase by 10%
    - increase orders by 10%
    - AOV decreases by 5%
    - reduce RTO by 20%
    - CAC improves by 10%

    Direction is determined only from the clause surrounding
    that metric, rather than from unrelated text later in
    the question.
    """

    metric_match = (
        _find_metric_position(
            question,
            aliases,
        )
    )

    if metric_match is None:
        return None

    q = question.lower()

    metric_position, alias = (
        metric_match
    )

    # --------------------------------------------------------
    # Determine the local clause boundaries.
    #
    # Split on commas and conjunctions so that:
    #
    # orders increase by 10%,
    # AOV increases by 5%,
    # and RTO reduces by 20%
    #
    # becomes three independent metric clauses.
    # --------------------------------------------------------

    clause_boundaries = [
        0,
    ]

    for match in re.finditer(
        r",|\band\b|\bwhile\b|\bbut\b|\bthen\b",
        q,
    ):
        clause_boundaries.append(
            match.start()
        )
        clause_boundaries.append(
            match.end()
        )

    clause_boundaries.append(
        len(q)
    )

    clause_start = 0
    clause_end = len(q)

    for index in range(
        len(clause_boundaries) - 1
    ):

        start = (
            clause_boundaries[
                index
            ]
        )

        end = (
            clause_boundaries[
                index + 1
            ]
        )

        if (
            start
            <= metric_position
            <= end
        ):
            clause_start = start
            clause_end = end
            break

    clause = q[
        clause_start:
        clause_end
    ]

    # --------------------------------------------------------
    # First look for percentage inside the metric clause.
    # --------------------------------------------------------

    percentage_matches = list(
        re.finditer(
            r"(-?\d+(?:\.\d+)?)\s*%",
            clause,
        )
    )

    if not percentage_matches:

        # Fallback: inspect a tight metric-local window.
        local_start = max(
            0,
            metric_position - 35,
        )

        local_end = min(
            len(q),
            metric_position
            + len(alias)
            + 55,
        )

        clause = q[
            local_start:
            local_end
        ]

        percentage_matches = list(
            re.finditer(
                r"(-?\d+(?:\.\d+)?)\s*%",
                clause,
            )
        )

    if not percentage_matches:
        return None

    # Metric clauses should normally contain one percentage.
    # Choose the percentage nearest the metric text if more
    # than one remains.
    metric_in_clause = (
        clause.find(
            alias.lower()
        )
    )

    if metric_in_clause < 0:
        metric_in_clause = 0

    nearest_match = min(
        percentage_matches,
        key=lambda match: abs(
            match.start()
            - metric_in_clause
        ),
    )

    value = float(
        nearest_match.group(1)
    )

    if value < 0:
        return value

    direction = (
        _direction_from_phrase(
            clause
        )
    )

    if direction is None:
        direction = 1

    return (
        abs(value)
        * direction
    )


# ============================================================
# PUBLIC SCENARIO PARSER
# ============================================================


def parse_scenario_question(
    question: str,
):
    """
    Parse natural-language scenario questions into
    deterministic scenario-engine parameters.

    Supported:
    - lost-order recovery
    - order percentage change
    - AOV percentage change
    - combined orders + AOV
    - RTO reduction
    - marketing-spend change
    - CAC change
    - multi-variable D2C scenarios
    """

    if not isinstance(
        question,
        str,
    ):
        return {
            "status": "invalid_question",
        }

    q = (
        question
        .lower()
        .strip()
    )

    if not q:
        return {
            "status": "invalid_question",
        }

    # ========================================================
    # LOST ORDER RECOVERY
    # ========================================================

    if (
        "recover" in q
        and "order" in q
    ):

        percentage = (
            _extract_percentage(
                question
            )
        )

        fraction = (
            _extract_recovery_fraction(
                question
            )
        )

        recovery_percent = (
            percentage
            if percentage is not None
            else fraction
        )

        if recovery_percent is None:

            return {
                "status": "missing_parameter",
                "scenario_type": (
                    "order_recovery"
                ),
                "missing": [
                    "recovery_percent",
                ],
            }

        return {
            "status": "complete",

            "scenario_type": (
                "order_recovery"
            ),

            "parameters": {
                "recovery_percent": abs(
                    recovery_percent
                ),
            },
        }

    # ========================================================
    # EXTRACT EACH METRIC INDEPENDENTLY
    # ========================================================

    order_change = (
        _extract_metric_change(
            question,
            [
                "order volume",
                "order count",
                "orders",
                "order",
            ],
        )
    )

    aov_change = (
        _extract_metric_change(
            question,
            [
                "average order value",
                "aov",
            ],
        )
    )

    rto_change = (
        _extract_metric_change(
            question,
            [
                "rto rate",
                "rto",
            ],
        )
    )

    marketing_spend_change = (
        _extract_metric_change(
            question,
            [
                "marketing spend",
                "marketing budget",
                "advertising spend",
                "ad spend",
            ],
        )
    )

    cac_change = (
        _extract_metric_change(
            question,
            [
                "customer acquisition cost",
                "cac",
            ],
        )
    )

    # ========================================================
    # NORMALIZE RTO
    # ========================================================

    rto_reduction_percent = None

    if rto_change is not None:

        if rto_change < 0:

            rto_reduction_percent = abs(
                rto_change
            )

        elif any(
            term in q
            for term in [
                "rto improve",
                "rto improves",
                "rto improved",
            ]
        ):

            rto_reduction_percent = abs(
                rto_change
            )

    # ========================================================
    # MULTI-METRIC D2C SCENARIO
    # ========================================================

    active_metrics = sum(
        value is not None
        for value in [
            order_change,
            aov_change,
            rto_reduction_percent,
            marketing_spend_change,
        ]
    )

    if active_metrics >= 2:

        return {
            "status": "complete",

            "scenario_type": (
                "d2c_combined_change"
            ),

            "parameters": {
                "order_change_percent": (
                    order_change
                    if order_change
                    is not None
                    else 0.0
                ),

                "aov_change_percent": (
                    aov_change
                    if aov_change
                    is not None
                    else 0.0
                ),

                "rto_reduction_percent": (
                    rto_reduction_percent
                    if rto_reduction_percent
                    is not None
                    else 0.0
                ),

                "marketing_spend_change_percent": (
                    marketing_spend_change
                    if marketing_spend_change
                    is not None
                    else 0.0
                ),
            },
        }

    # ========================================================
    # RTO REDUCTION
    # ========================================================

    if (
        "rto" in q
        and rto_reduction_percent
        is not None
    ):

        return {
            "status": "complete",

            "scenario_type": (
                "rto_reduction"
            ),

            "parameters": {
                "rto_reduction_percent": (
                    rto_reduction_percent
                ),
            },
        }

    # ========================================================
    # MARKETING SPEND
    # ========================================================

    if (
        marketing_spend_change
        is not None
    ):

        return {
            "status": "complete",

            "scenario_type": (
                "marketing_spend_change"
            ),

            "parameters": {
                "marketing_spend_change_percent": (
                    marketing_spend_change
                ),
            },
        }

    # ========================================================
    # CAC
    # ========================================================

    if cac_change is not None:

        return {
            "status": "complete",

            "scenario_type": (
                "cac_change"
            ),

            "parameters": {
                "cac_change_percent": (
                    cac_change
                ),
            },
        }

    # ========================================================
    # AOV ONLY
    # ========================================================

    if (
        "aov" in q
        or "average order value" in q
    ):

        if aov_change is None:

            return {
                "status": "missing_parameter",

                "scenario_type": (
                    "aov_change"
                ),

                "missing": [
                    "aov_change_percent",
                ],
            }

        return {
            "status": "complete",

            "scenario_type": (
                "aov_change"
            ),

            "parameters": {
                "aov_change_percent": (
                    aov_change
                ),
            },
        }

    # ========================================================
    # ORDERS ONLY
    # ========================================================

    if (
        "order" in q
        or "orders" in q
    ):

        if order_change is None:

            return {
                "status": "missing_parameter",

                "scenario_type": (
                    "combined_change"
                ),

                "missing": [
                    "order_change_percent",
                ],
            }

        return {
            "status": "complete",

            "scenario_type": (
                "combined_change"
            ),

            "parameters": {
                "order_change_percent": (
                    order_change
                ),
                "aov_change_percent": 0.0,
            },
        }

    # ========================================================
    # UNSUPPORTED
    # ========================================================

    return {
        "status": (
            "unsupported_scenario"
        ),

        "message": (
            "The scenario question could not be mapped "
            "to a supported deterministic scenario."
        ),

        "supported_scenarios": [
            "order recovery",
            "order percentage change",
            "AOV percentage change",
            "combined order and AOV change",
            "RTO reduction",
            "marketing spend change",
            "CAC change",
            "combined D2C scenarios",
        ],
    }
import re


def _extract_percentage(question: str):
    """
    Extract the first percentage value from a question.

    Examples:
    "increase AOV by 5%" -> 5.0
    "decrease orders by 10%" -> 10.0
    """

    match = re.search(
        r"(-?\d+(?:\.\d+)?)\s*%",
        question
    )

    if not match:
        return None

    return float(
        match.group(1)
    )


def _extract_recovery_fraction(question: str):
    """
    Understand simple recovery language.

    Examples:
    half -> 50
    quarter -> 25
    three quarters -> 75
    all -> 100
    """

    q = question.lower()

    if "half" in q:
        return 50.0

    if "quarter" in q:
        return 25.0

    if (
        "three quarters" in q
        or "three-quarters" in q
    ):
        return 75.0

    if (
        "all lost" in q
        or "all of the lost" in q
        or "fully recover" in q
        or "recover all" in q
    ):
        return 100.0

    return None


def _detect_direction(
    question: str
):
    """
    Detect whether the user is describing
    an increase or decrease.
    """

    q = question.lower()

    decrease_terms = [
        "decrease",
        "decreases",
        "decreased",
        "decline",
        "declines",
        "declined",
        "drop",
        "drops",
        "reduce",
        "reduces",
        "reduced",
        "fall",
        "falls",
        "fell",
        "lower",
    ]

    increase_terms = [
        "increase",
        "increases",
        "increased",
        "improve",
        "improves",
        "improved",
        "grow",
        "grows",
        "grew",
        "rise",
        "rises",
        "rose",
        "higher",
        "recover",
        "recovery",
    ]

    if any(
        term in q
        for term in decrease_terms
    ):
        return -1

    if any(
        term in q
        for term in increase_terms
    ):
        return 1

    return None


def parse_scenario_question(
    question: str
):
    """
    Parse a scenario question into deterministic
    parameters for the scenario engine.
    """

    if not isinstance(
        question,
        str
    ):
        return {
            "status": "invalid_question",
        }

    q = question.lower().strip()

    percentage = (
        _extract_percentage(
            question
        )
    )

    recovery_fraction = (
        _extract_recovery_fraction(
            question
        )
    )

    direction = (
        _detect_direction(
            question
        )
    )

    # --------------------------------------------------
    # ORDER RECOVERY
    # --------------------------------------------------

    if (
        "recover" in q
        and (
            "order" in q
            or "orders" in q
        )
    ):

        recovery_percent = (
            percentage
            if percentage is not None
            else recovery_fraction
        )

        if recovery_percent is None:

            return {
                "status": "missing_parameter",
                "scenario_type": "order_recovery",
                "missing": [
                    "recovery_percent"
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
                )
            },
        }

    # --------------------------------------------------
    # AOV CHANGE
    # --------------------------------------------------

    if (
        "aov" in q
        or "average order value" in q
    ):

        if percentage is None:

            return {
                "status": "missing_parameter",
                "scenario_type": "aov_change",
                "missing": [
                    "aov_change_percent"
                ],
            }

        if direction is None:
            direction = 1

        return {
            "status": "complete",
            "scenario_type": "aov_change",
            "parameters": {
                "aov_change_percent": (
                    abs(percentage)
                    * direction
                )
            },
        }

    # --------------------------------------------------
    # ORDER CHANGE
    # --------------------------------------------------

    if (
        "order" in q
        or "orders" in q
    ):

        if percentage is None:

            return {
                "status": "missing_parameter",
                "scenario_type": (
                    "combined_change"
                ),
                "missing": [
                    "order_change_percent"
                ],
            }

        if direction is None:
            direction = 1

        return {
            "status": "complete",
            "scenario_type": (
                "combined_change"
            ),
            "parameters": {
                "order_change_percent": (
                    abs(percentage)
                    * direction
                ),
                "aov_change_percent": 0,
            },
        }

    # --------------------------------------------------
    # COMBINED ORDERS + AOV
    # --------------------------------------------------

    if (
        "orders" in q
        and "aov" in q
    ):

        percentages = re.findall(
            r"(-?\d+(?:\.\d+)?)\s*%",
            question
        )

        if len(
            percentages
        ) < 2:

            return {
                "status": "missing_parameter",
                "scenario_type": (
                    "combined_change"
                ),
                "missing": [
                    "order_change_percent",
                    "aov_change_percent",
                ],
            }

        order_percent = float(
            percentages[0]
        )

        aov_percent = float(
            percentages[1]
        )

        return {
            "status": "complete",
            "scenario_type": (
                "combined_change"
            ),
            "parameters": {
                "order_change_percent": (
                    order_percent
                ),
                "aov_change_percent": (
                    aov_percent
                ),
            },
        }

    # --------------------------------------------------
    # UNSUPPORTED
    # --------------------------------------------------

    return {
        "status": "unsupported_scenario",

        "message": (
            "The scenario question could not be mapped "
            "to a currently supported deterministic "
            "scenario."
        ),

        "supported_scenarios": [
            "order recovery",
            "order percentage change",
            "AOV percentage change",
            "combined order and AOV change",
        ],
    }
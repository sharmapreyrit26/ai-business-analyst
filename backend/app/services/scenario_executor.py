from backend.app.services.scenario_parser import (
    parse_scenario_question,
)

from backend.app.services.scenario_engine import (
    run_scenario,
)


def execute_scenario_question(
    question: str,
    month: str
):
    """
    Parse and execute a natural-language
    scenario deterministically.
    """

    parsed = parse_scenario_question(
        question
    )

    if (
        parsed.get("status")
        != "complete"
    ):

        return {
            "question": question,
            "month": month,
            "status": parsed.get(
                "status"
            ),
            "parser_result": parsed,
            "scenario_result": None,
        }

    scenario_type = parsed[
        "scenario_type"
    ]

    parameters = parsed.get(
        "parameters",
        {}
    )

    result = run_scenario(
        month,
        scenario_type,
        **parameters
    )

    return {
        "question": question,
        "month": month,
        "status": result.get(
            "status",
            "complete"
        ),
        "scenario_type": (
            scenario_type
        ),
        "parameters": parameters,
        "scenario_result": result,
    }
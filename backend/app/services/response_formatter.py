def format_business_answer(
    question: str,
    month: str,
    question_type: str,
    context: dict,
    answer: dict
):
    """
    Standardize the final response returned by the AI Business Analyst.

    The analytics/context layer remains responsible for calculations.
    The LLM remains responsible for interpretation.
    This layer only normalizes the final API response.
    """

    if not isinstance(answer, dict):
        answer = {
            "answer": str(answer),
            "evidence": [],
            "likely_driver": None,
            "recommended_actions": []
        }

    summary = answer.get(
        "answer",
        answer.get("summary", "")
    )

    evidence = answer.get("evidence", [])
    likely_driver = answer.get("likely_driver")
    recommended_actions = answer.get(
        "recommended_actions",
        []
    )

    # Ensure consistent types
    if not isinstance(evidence, list):
        evidence = [str(evidence)]

    if not isinstance(recommended_actions, list):
        recommended_actions = [
            str(recommended_actions)
        ]

    return {
        "question": question,
        "month": month,
        "question_type": question_type,

        "answer": {
            "summary": summary,
            "evidence": evidence,
            "likely_driver": likely_driver,
            "recommended_actions": recommended_actions
        }
    }
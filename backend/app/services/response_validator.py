REQUIRED_FIELDS = {
    "answer": str,
    "evidence": list,
    "likely_driver": str,
    "recommended_actions": list,
}


def validate_business_response(response: dict) -> dict:
    """
    Validate the structure of an AI business analyst response.
    """

    if not isinstance(response, dict):
        raise ValueError("AI response must be a dictionary.")

    for field, expected_type in REQUIRED_FIELDS.items():

        if field not in response:
            raise ValueError(
                f"AI response missing required field: {field}"
            )

        if not isinstance(response[field], expected_type):
            raise ValueError(
                f"AI response field '{field}' must be "
                f"{expected_type.__name__}."
            )

    return response
REQUIRED_FIELDS = {
    "answer": str,
    "evidence": list,
    "likely_driver": str,
}


def validate_business_response(
    response: dict,
    *,
    require_recommended_actions: bool = True,
) -> dict:
    """
    Validate the structure of an AI business analyst response.

    D2C:
    - recommended_actions are owned by the deterministic
      recommendation gate, so the LLM field is optional.

    Legacy:
    - recommended_actions remain required temporarily for
      backwards compatibility.
    """

    if not isinstance(
        response,
        dict,
    ):
        raise ValueError(
            "AI response must be a dictionary."
        )

    required_fields = dict(
        REQUIRED_FIELDS
    )

    if require_recommended_actions:
        required_fields[
            "recommended_actions"
        ] = list

    for (
        field,
        expected_type,
    ) in required_fields.items():

        if field not in response:
            raise ValueError(
                f"AI response missing required field: {field}"
            )

        if not isinstance(
            response[field],
            expected_type,
        ):
            raise ValueError(
                f"AI response field '{field}' must be "
                f"{expected_type.__name__}."
            )

    if (
        "recommended_actions"
        in response
        and not isinstance(
            response[
                "recommended_actions"
            ],
            list,
        )
    ):
        raise ValueError(
            "AI response field 'recommended_actions' "
            "must be list when present."
        )

    return response

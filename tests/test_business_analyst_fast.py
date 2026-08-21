from unittest.mock import patch

from backend.app.services.business_analyst import (
    answer_business_question,
)


TEST_CASES = [
    (
        "Why did revenue decline?",
        "revenue",
    ),
    (
        "How did orders perform?",
        "orders",
    ),
    (
        "What is our delivery rate?",
        "delivery",
    ),
    (
        "What is our cancellation rate?",
        "cancellation",
    ),
    (
        "Which products generated the most revenue?",
        "product",
    ),
    (
        "What is our repeat purchase rate?",
        "customer",
    ),
    (
        "What is our P90 delivery TAT?",
        "logistics",
    ),
    (
        "What if AOV increases by 12%?",
        "scenario",
    ),
    (
        "Why did revenue decline even though delivery improved?",
        "general_business",
    ),
]


@patch(
    "backend.app.services.business_analyst."
    "ask_business_analyst"
)
def test_fast_business_analyst(
    mock_ai,
):
    """
    Test the complete interactive analytical pipeline
    without making external Gemini requests.

    The AI response is mocked so tests validate:
    - routing
    - deterministic analysis
    - response structure
    - API contract

    without depending on network latency or quota.
    """

    mock_ai.return_value = {
        "answer": (
            "Mock AI interpretation."
        ),
        "evidence": [
            "Mock evidence."
        ],
        "likely_driver": (
            "Mock driver"
        ),
        "recommended_actions": [],
    }

    for (
        question,
        expected_type,
    ) in TEST_CASES:

        result = (
            answer_business_question(
                question=question,
                month="2018-06",
            )
        )

        assert (
            result["question_type"]
            == expected_type
        ), (
            f"Wrong intent for: {question}. "
            f"Expected {expected_type}, "
            f"got {result['question_type']}"
        )

        assert (
            result[
                "analysis_execution"
            ][
                "successful_steps"
            ]
            == 1
        )

        assert (
            result[
                "analysis_execution"
            ][
                "failed_steps"
            ]
            == 0
        )

        assert (
            result["ai_available"]
            is True
        )

        answer = result.get(
            "answer",
            {}
        )

        assert isinstance(
            answer,
            dict
        )

        assert answer.get(
            "answer"
        )

        assert isinstance(
            answer.get(
                "evidence",
                []
            ),
            list,
        )

        assert (
            "likely_driver"
            in answer
        )

        assert isinstance(
            answer.get(
                "recommended_actions",
                []
            ),
            list,
        )


@patch(
    "backend.app.services.business_analyst."
    "ask_business_analyst"
)
def test_ai_failure_uses_fallback(
    mock_ai,
):
    """
    Verify ProfitLens still returns an answer
    when the external AI service fails.
    """

    mock_ai.side_effect = (
        RuntimeError(
            "AI unavailable"
        )
    )

    result = (
        answer_business_question(
            question=(
                "Why did revenue decline?"
            ),
            month="2018-06",
        )
    )

    assert (
        result["question_type"]
        == "revenue"
    )

    assert (
        result["ai_available"]
        is False
    )

    answer = result[
        "answer"
    ]

    assert answer[
        "answer"
    ]

    assert len(
        answer["evidence"]
    ) >= 1

    assert (
        "likely_driver"
        in answer
    )
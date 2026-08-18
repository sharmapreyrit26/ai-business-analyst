from backend.app.services.question_router import classify_question
from backend.app.services.context_builder import build_context
from backend.app.services.insight_engine import generate_business_insights
from backend.app.services.llm_service import ask_business_analyst


def _build_deterministic_fallback(
    question: str,
    month: str,
    question_type: str,
    insights: dict
) -> dict:
    """
    Build a deterministic response when the AI service
    is unavailable.

    This allows the Business Analyst to continue functioning
    even when the external LLM API is unavailable.
    """

    selected_insight = None

    for insight in insights.get("insights", []):

        if question_type == "revenue" and "revenue_change_percent" in insight:
            selected_insight = insight
            break

        if question_type == "orders" and "order_change_percent" in insight:
            selected_insight = insight
            break

        if question_type == "delivery" and "delivery_rate_percent" in insight:
            selected_insight = insight
            break

        if (
            question_type == "cancellation"
            and "cancellation_rate_percent" in insight
        ):
            selected_insight = insight
            break

        if question_type == "performance" and "overall_status" in insight:
            selected_insight = insight
            break

    # --------------------------------
    # FALLBACK ANSWER
    # --------------------------------

    if selected_insight:

        summary = selected_insight.get(
            "summary",
            "Business insight is available."
        )

        evidence = []

        for key, value in selected_insight.items():

            if key in {
                "period",
                "summary",
                "data_quality"
            }:
                continue

            if isinstance(value, (int, float, str)):

                evidence.append(
                    f"{key.replace('_', ' ').capitalize()}: {value}"
                )

        return {
            "answer": summary,
            "evidence": evidence[:5],
            "likely_driver": selected_insight.get(
                "primary_driver",
                "Not applicable"
            ),
            "recommended_actions": []
        }

    # --------------------------------
    # GENERIC FALLBACK
    # --------------------------------

    return {
        "answer": (
            f"Deterministic business analysis is available "
            f"for {month}, but an AI-generated interpretation "
            f"is currently unavailable."
        ),
        "evidence": [],
        "likely_driver": "Not available",
        "recommended_actions": []
    }


def answer_business_question(
    question: str,
    month: str = "2018-06"
) -> dict:
    """
    End-to-end AI Business Analyst pipeline.

    Flow:

    1. Classify the user's natural-language question.
    2. Build deterministic business context.
    3. Generate deterministic business insights.
    4. Ask the LLM to interpret the analysis.
    5. Fall back to deterministic insights if the LLM
       is unavailable.
    """

    # --------------------------------
    # 1. CLASSIFY QUESTION
    # --------------------------------

    question_type = classify_question(question)

    # --------------------------------
    # 2. BUILD BUSINESS CONTEXT
    # --------------------------------

    business_context = build_context(
        question_type,
        month
    )

    # --------------------------------
    # 3. GENERATE DETERMINISTIC INSIGHTS
    # --------------------------------

    deterministic_insights = (
        generate_business_insights(month)
    )

    # Add deterministic insights to the
    # context available to the AI.

    business_context["deterministic_insights"] = (
        deterministic_insights
    )

    # --------------------------------
    # 4. ASK AI ANALYST
    # --------------------------------

    try:

        answer = ask_business_analyst(
            question=question,
            question_type=question_type,
            month=month,
            business_context=business_context
        )

        ai_available = True

    except Exception:

        # --------------------------------
        # 5. DETERMINISTIC FALLBACK
        # --------------------------------

        answer = _build_deterministic_fallback(
            question=question,
            month=month,
            question_type=question_type,
            insights=deterministic_insights
        )

        ai_available = False

    # --------------------------------
    # 6. RETURN FINAL RESPONSE
    # --------------------------------

    return {
        "question": question,
        "month": month,
        "question_type": question_type,
        "ai_available": ai_available,
        "answer": answer
    }
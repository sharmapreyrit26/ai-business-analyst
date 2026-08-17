from backend.app.services.question_router import classify_question
from backend.app.services.context_builder import build_context
from backend.app.services.llm_service import ask_business_analyst


def answer_business_question(
    question: str,
    month: str = "2018-06"
) -> dict:
    """
    End-to-end AI Business Analyst pipeline.

    Flow:
    1. Classify the user's natural-language question.
    2. Build deterministic business context.
    3. Ask the LLM to interpret that context.
    4. Return the structured business answer.
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
    # 3. ASK BUSINESS ANALYST
    # --------------------------------

    answer = ask_business_analyst(
        question=question,
        question_type=question_type,
        month=month,
        business_context=business_context
    )

    # --------------------------------
    # 4. RETURN FINAL RESPONSE
    # --------------------------------

    return {
        "question": question,
        "month": month,
        "question_type": question_type,
        "answer": answer
    }
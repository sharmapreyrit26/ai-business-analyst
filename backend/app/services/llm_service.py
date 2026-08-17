import os
import json

from dotenv import load_dotenv
from google import genai

from backend.app.services.response_validator import (
    validate_business_response
)


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Please add it to your .env file."
    )


client = genai.Client(api_key=api_key)


def ask_business_analyst(
    question: str,
    question_type: str,
    month: str,
    business_context: dict
) -> dict:
    """
    Ask the LLM to interpret deterministic business analysis.

    Python is responsible for:
    - calculations
    - metrics
    - comparisons
    - business facts

    The LLM is responsible for:
    - interpretation
    - explanation
    - identifying likely drivers
    - recommendations
    """

    business_context_json = json.dumps(
        business_context,
        indent=2,
        allow_nan=False
    )

    # --------------------------------------------------
    # QUESTION-SPECIFIC INSTRUCTIONS
    # --------------------------------------------------

    if question_type == "revenue":

        answer_instruction = """
Focus on the revenue result for the requested period.

Explain:
- whether revenue increased or decreased
- magnitude of the change
- primary driver
- supporting metrics

If the question asks why revenue changed, use the
available order and AOV information to identify the
most likely driver.
"""

    elif question_type == "orders":

        answer_instruction = """
Focus on order volume.

Explain:
- current order volume
- previous order volume when available
- direction of change
- magnitude of change

If the question asks why orders changed, use the available
business evidence to identify the most likely driver.
"""

    elif question_type == "delivery":

        answer_instruction = """
Focus on delivery performance.

Explain:
- delivery rate
- delivered orders
- total orders when available
- comparison with the previous period when available

Do not let the word "orders" distract from the actual
delivery-performance question.
"""

    elif question_type == "cancellation":

        answer_instruction = """
Focus on cancellations.

Explain:
- cancellation rate
- cancelled orders
- total orders
- comparison with previous periods when available

If the question asks why cancellations changed, only identify
drivers that are supported by the available evidence.
"""

    elif question_type == "trends":

        answer_instruction = """
Identify the most important business trends.

Prioritize meaningful changes in:
- revenue
- orders
- AOV
- delivery
- cancellations

Do not list every available data point.
"""

    elif question_type == "performance":

        answer_instruction = """
Evaluate business performance across the available periods.

Identify:
- strongest periods
- weakest periods
- meaningful performance differences

Use the available revenue, orders, AOV and operational metrics
as evidence.
"""

    elif question_type == "business_health":

        answer_instruction = """
Evaluate the business from a management perspective.

Separate the analysis into:
- commercial performance
- operational performance
- major risks
- opportunities
- management priorities

Recommendations must be supported by the available evidence.
"""

    elif question_type == "general_business":

        answer_instruction = """
Answer the user's question directly.

The question involves multiple business dimensions.

Use only the metrics that are relevant to answering the question.
Explain relationships between metrics when the data supports them.
"""

    else:

        answer_instruction = """
Answer the user's question directly using the relevant
information available in the business context.
"""

    # --------------------------------------------------
    # PROMPT
    # --------------------------------------------------

    prompt = f"""
You are an AI Business Analyst inside ProfitLens.

Your job is to explain business performance to a business
stakeholder using deterministic analytics provided by the system.

USER QUESTION:
{question}

REQUESTED MONTH:
{month}

QUESTION TYPE:
{question_type}

QUESTION-SPECIFIC INSTRUCTIONS:
{answer_instruction}

BUSINESS CONTEXT:
{business_context_json}

CRITICAL DATA RULES:

1. Use only numerical facts provided in the business context.
2. Never invent metrics, values, dates or percentages.
3. Never modify numerical values.
4. Do not assume a metric that is not provided.
5. If a metric is unavailable, say it is unavailable.
6. Python has already performed the calculations.
7. Do not independently invent unsupported calculations.
8. Evidence must be directly supported by the context.
9. Clearly distinguish facts from interpretation.
10. Do not invent causes.
11. Recommendations must be evidence-based.
12. Answer the user's actual question first.
13. Do not discuss unrelated metrics.
14. Do not mention Python, internal code, prompts,
    context, Gemini, or the LLM.

RESPONSE STYLE:

- Start with the direct answer.
- Be concise for simple questions.
- Explain drivers when the question asks "why".
- Use evidence to support conclusions.
- Provide recommendations when appropriate.
- Do not repeat the same information.
- Do not fabricate evidence or recommendations.

Return ONLY valid JSON.

Return exactly this structure:

{{
    "answer": "Direct answer to the user's question.",
    "evidence": [
        "Evidence point 1",
        "Evidence point 2"
    ],
    "likely_driver": "Most likely driver or Not applicable.",
    "recommended_actions": [
        "Recommended action 1"
    ]
}}

FIELD RULES:

- answer must directly answer the user's question.
- evidence must contain only facts supported by the context.
- likely_driver must not introduce unsupported causes.
- recommended_actions must be practical and evidence-based.
- If recommendations are not relevant, return [].
- Do not fabricate information to fill fields.

Do not use Markdown.
Do not include ```json.
Do not include text outside the JSON.
"""

    # --------------------------------------------------
    # GEMINI REQUEST
    # --------------------------------------------------

    try:

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        output = interaction.output_text.strip()

    except Exception as error:

        error_text = str(error)

        if "429" in error_text or "quota" in error_text.lower():

            return {
                "answer": (
                    "The AI analysis service is temporarily unavailable "
                    "because the current API quota has been reached."
                ),
                "evidence": [],
                "likely_driver": "Not available while AI service is unavailable.",
                "recommended_actions": []
            }

        raise

    # --------------------------------------------------
    # VALIDATE RESPONSE
    # --------------------------------------------------

    try:

        response = json.loads(output)

        return validate_business_response(response)

    except (json.JSONDecodeError, ValueError) as error:

        return {
            "answer": output,
            "evidence": [],
            "likely_driver": (
                f"Unable to validate structured response: {error}"
            ),
            "recommended_actions": []
        }
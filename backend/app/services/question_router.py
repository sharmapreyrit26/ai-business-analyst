import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Please add it to your .env file."
    )


client = genai.Client(api_key=api_key)


SUPPORTED_INTENTS = {
    "revenue": (
        "Questions about revenue, sales, income, earnings, turnover, "
        "revenue growth or decline, or why revenue changed."
    ),

    "orders": (
        "Questions about order volume, number of orders, order growth, "
        "declining or increasing orders, or customer order frequency."
    ),

    "delivery": (
        "Questions about delivery performance, delivery rate, successful "
        "deliveries, fulfillment performance, or delivery improvement."
    ),

    "cancellation": (
        "Questions about cancelled orders, cancellation rate, or reasons "
        "related to cancellations."
    ),

    "trends": (
        "Questions asking about trends, patterns, changes over time, "
        "major movements, or emerging business patterns."
    ),

    "performance": (
        "Questions about overall business performance, monthly performance, "
        "best or worst performing periods, or performance comparison."
    ),

    "business_health": (
        "Questions asking for overall business health, management priorities, "
        "risks, recommendations, what should be improved, or what the "
        "business should do next."
    ),

    "general_business": (
        "Business questions involving multiple metrics or multiple areas "
        "such as revenue, orders, delivery, cancellations, and performance."
    ),

    "general": (
        "A broad question that does not clearly belong to one of the "
        "specific business categories above."
    ),
}


def _deterministic_intent(question: str):
    """
    Handle obvious semantic cases before sending the question to the LLM.

    Returns:
        str | None
        The intent if confidently identified, otherwise None.
    """

    q = question.lower().strip()

    # ---------------------------------------------------------
    # MULTI-METRIC / COMPARISON QUESTIONS
    # ---------------------------------------------------------

    revenue_terms = [
        "revenue",
        "sales",
        "income",
        "earnings",
        "turnover",
        "money",
        "made less",
        "made more",
    ]

    order_terms = [
        "order volume",
        "number of orders",
        "order count",
        "orders",
        "buying",
        "purchase",
        "purchases",
        "ordering",
    ]

    delivery_terms = [
        "delivery",
        "deliveries",
        "delivered",
        "delivering",
        "fulfillment",
        "shipping performance",
    ]

    cancellation_terms = [
        "cancel",
        "cancelled",
        "canceled",
        "cancellation",
        "cancellations",
    ]

    trend_terms = [
        "trend",
        "trends",
        "pattern",
        "patterns",
        "over time",
        "emerging",
    ]

    # If a question explicitly compares multiple business areas,
    # it is a general business question.

    matched_dimensions = []

    if any(term in q for term in revenue_terms):
        matched_dimensions.append("revenue")

    if any(term in q for term in order_terms):
        matched_dimensions.append("orders")

    if any(term in q for term in delivery_terms):
        matched_dimensions.append("delivery")

    if any(term in q for term in cancellation_terms):
        matched_dimensions.append("cancellation")

    # Important:
    # "delivering orders" should NOT become orders.
    #
    # Example:
    # "Are we getting better at delivering orders?"
    #
    # The subject is delivery performance, not order volume.

    delivery_phrases = [
        "delivering orders",
        "delivery performance",
        "delivery rate",
        "delivery success",
        "successful deliveries",
        "deliveries improving",
        "deliveries getting better",
        "deliveries getting worse",
        "delivery improving",
        "delivery getting better",
        "delivery getting worse",
    ]

    if any(phrase in q for phrase in delivery_phrases):

        # If cancellation or revenue is also involved,
        # this is a multi-dimensional question.

        if (
            "cancellation" in matched_dimensions
            or "revenue" in matched_dimensions
        ):
            return "general_business"

        return "delivery"

    # Questions explicitly involving cancellations + another
    # business dimension should be treated as general_business.

    if "cancellation" in matched_dimensions:

        other_dimensions = [
            dimension
            for dimension in matched_dimensions
            if dimension != "cancellation"
        ]

        if other_dimensions:
            return "general_business"

        # "Why are orders being cancelled?" involves the order
        # process and cancellations, so treat it as broader
        # business analysis.

        if "orders" in q:
            return "general_business"

        return "cancellation"

    # Revenue + another metric = general business.

    if "revenue" in matched_dimensions:

        other_dimensions = [
            dimension
            for dimension in matched_dimensions
            if dimension != "revenue"
        ]

        if other_dimensions:
            return "general_business"

    # Orders + another metric = general business.

    if "orders" in matched_dimensions:

        other_dimensions = [
            dimension
            for dimension in matched_dimensions
            if dimension != "orders"
        ]

        if other_dimensions:
            return "general_business"

    # ---------------------------------------------------------
    # BUSINESS HEALTH
    # ---------------------------------------------------------

    business_health_phrases = [
        "what should we do",
        "what should management do",
        "what should management focus on",
        "management focus",
        "what should we improve",
        "how can we improve",
        "how should we improve",
        "what should we prioritize",
        "what should management prioritize",
        "business health",
        "business risk",
        "business risks",
        "next step",
        "next steps",
        "recommendation",
        "recommendations",
        "what should we focus on",
    ]

    if any(phrase in q for phrase in business_health_phrases):
        return "business_health"

    # ---------------------------------------------------------
    # TRENDS
    # ---------------------------------------------------------

    trend_phrases = [
        "what trends",
        "major trends",
        "business trends",
        "what patterns",
        "major patterns",
        "patterns are you seeing",
        "trends are you seeing",
        "over time",
        "emerging trends",
    ]

    if any(phrase in q for phrase in trend_phrases):
        return "trends"

    # ---------------------------------------------------------
    # PERFORMANCE
    # ---------------------------------------------------------

    performance_phrases = [
        "best month",
        "worst month",
        "best period",
        "worst period",
        "which month performed",
        "which period performed",
        "monthly performance",
        "overall performance",
        "how is the business performing",
        "how are we performing",
    ]

    if any(phrase in q for phrase in performance_phrases):
        return "performance"

    # No confident deterministic classification.
    return None


def _keyword_fallback(question: str) -> str:

    q = question.lower().strip()

    revenue_keywords = [
        "revenue",
        "sales",
        "income",
        "earnings",
        "turnover",
        "money",
        "made less",
        "made more",
    ]

    order_keywords = [
        "order volume",
        "order count",
        "number of orders",
        "orders",
        "buying",
        "purchase",
        "purchases",
        "ordering",
    ]

    delivery_keywords = [
        "delivery",
        "deliveries",
        "delivered",
        "delivering",
        "fulfillment",
        "shipping performance",
    ]

    cancellation_keywords = [
        "cancel",
        "cancelled",
        "canceled",
        "cancellation",
        "cancellations",
    ]

    trend_keywords = [
        "trend",
        "trends",
        "pattern",
        "patterns",
        "over time",
        "emerging",
    ]

    performance_keywords = [
        "performance",
        "performing",
        "best month",
        "worst month",
        "best period",
        "worst period",
        "monthly performance",
        "which month",
        "which period",
    ]

    business_health_keywords = [
        "business health",
        "what should we do",
        "what should we improve",
        "recommendation",
        "recommendations",
        "risk",
        "risks",
        "improve",
        "improvement",
        "next step",
        "next steps",
        "management focus",
        "focus on",
        "what should management",
        "what should we prioritize",
    ]

    matched_categories = []

    if any(keyword in q for keyword in revenue_keywords):
        matched_categories.append("revenue")

    if any(keyword in q for keyword in order_keywords):
        matched_categories.append("orders")

    if any(keyword in q for keyword in delivery_keywords):
        matched_categories.append("delivery")

    if any(keyword in q for keyword in cancellation_keywords):
        matched_categories.append("cancellation")

    if any(keyword in q for keyword in trend_keywords):
        matched_categories.append("trends")

    if any(keyword in q for keyword in performance_keywords):
        matched_categories.append("performance")

    if any(keyword in q for keyword in business_health_keywords):
        matched_categories.append("business_health")

    # Explicit delivery phrase protection.

    delivery_phrases = [
        "delivering orders",
        "delivery performance",
        "delivery rate",
        "successful deliveries",
        "deliveries improving",
        "deliveries getting better",
        "delivery improving",
        "delivery getting better",
        "delivery getting worse",
    ]

    if any(phrase in q for phrase in delivery_phrases):

        if any(
            keyword in q
            for keyword in revenue_keywords + cancellation_keywords
        ):
            return "general_business"

        return "delivery"

    # Multiple categories means multiple business dimensions.

    if len(matched_categories) > 1:
        return "general_business"

    if len(matched_categories) == 1:
        return matched_categories[0]

    return "general"


def classify_question(question: str) -> str:

    if not isinstance(question, str):
        return "general"

    question = question.strip()

    if not question:
        return "general"

    # ---------------------------------------------------------
    # STEP 1: DETERMINISTIC CLASSIFICATION
    # ---------------------------------------------------------

    deterministic_result = _deterministic_intent(question)

    if deterministic_result:
        return deterministic_result

    # ---------------------------------------------------------
    # STEP 2: LLM SEMANTIC CLASSIFICATION
    # ---------------------------------------------------------

    intent_descriptions = "\n".join(
        [
            f"- {intent}: {description}"
            for intent, description in SUPPORTED_INTENTS.items()
        ]
    )

    prompt = f"""
You are the intent classifier for an AI Business Analyst system.

Your job is to understand the semantic meaning of the user's question.

The user can ask ANY business question in natural language.

They do NOT need to use predefined wording.

Before selecting the final intent, identify the actual business
dimension being discussed.

SUPPORTED INTENTS:

{intent_descriptions}

IMPORTANT RULES:

1. Understand the meaning of the complete question.

2. Do NOT classify based only on individual keywords.

3. The word "orders" does NOT automatically mean the "orders" intent.

4. If the question is about delivering orders, delivery success,
   delivery rate, or delivery performance, classify it as "delivery".

5. Example:

   "Are we getting better at delivering orders?"

   -> delivery

6. Example:

   "Why are customers buying fewer products?"

   -> orders

7. If cancellations are involved together with another business
   dimension, classify as "general_business".

8. If the question compares two or more business metrics,
   classify as "general_business".

9. If revenue is compared with delivery, orders, cancellations,
   or another metric, classify as "general_business".

10. If only one business dimension is involved, return that
    specific intent.

11. If the user asks what management should do, priorities,
    recommendations, risks, improvements, or next steps,
    return "business_health".

12. If the question asks about trends or patterns,
    return "trends".

13. If the question asks about best/worst months or performance
    comparisons, return "performance".

14. If nothing clearly matches, return "general".

15. Never invent a new intent.

EXAMPLES:

"Why did revenue decline?"
-> revenue

"Why did we make less money last month?"
-> revenue

"Why are customers buying less?"
-> orders

"Why are customers placing fewer orders?"
-> orders

"Are we getting better at delivering orders?"
-> delivery

"Are our deliveries improving?"
-> delivery

"How successful are our deliveries?"
-> delivery

"Why are so many orders being cancelled?"
-> general_business

"Did cancellations increase?"
-> cancellation

"What patterns are you seeing?"
-> trends

"What are the major trends in the business?"
-> trends

"Which month performed the best?"
-> performance

"How is the business performing?"
-> performance

"What should management focus on?"
-> business_health

"How can we improve the business?"
-> business_health

"Why did revenue fall even though delivery improved?"
-> general_business

"Why did orders fall while cancellations increased?"
-> general_business

"Did revenue improve despite worse delivery?"
-> general_business

"How did revenue, orders and delivery perform?"
-> general_business

User question:

{question}

Return ONLY valid JSON.

Return exactly:

{{
    "intent": "one_supported_intent"
}}
"""

    try:

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        output = interaction.output_text.strip()

        response = json.loads(output)

        intent = response.get("intent")

        if intent in SUPPORTED_INTENTS:
            return intent

        return _keyword_fallback(question)

    except Exception:

        return _keyword_fallback(question)
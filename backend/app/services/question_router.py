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


client = genai.Client(
    api_key=api_key
)


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
        "Questions specifically about delivery success rate, delivered "
        "orders, fulfilment success, or whether delivery success is "
        "improving or worsening."
    ),

    "cancellation": (
        "Questions about cancelled orders, cancellation rate, or "
        "cancellations increasing or decreasing."
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

    "product": (
        "Questions about products, SKUs, product revenue, units sold, "
        "product mix, product concentration, best-selling products, "
        "product performance, freight burden by product, or "
        "product-level business analysis."
    ),

    "customer": (
        "Questions about customers, repeat purchase, retention, cohorts, "
        "customer behaviour, customer value, LTV, CAC, new customers, "
        "returning customers, or customer segmentation."
    ),

    "logistics": (
        "Questions about fulfilment, shipping, logistics, delivery TAT, "
        "carrier handover, promised delivery, late deliveries, freight, "
        "RTO, NDR, courier performance, COD versus prepaid, delivery SLA, "
        "or fulfilment turnaround time."
    ),

    "scenario": (
        "What-if or simulation questions asking what would happen if "
        "orders, AOV, revenue, RTO, conversion, price, marketing spend, "
        "or another business metric changed."
    ),

    "general_business": (
        "Business questions involving multiple business dimensions or "
        "multiple metrics such as revenue, orders, delivery, cancellations, "
        "products, customers, logistics, and performance."
    ),

    "general": (
        "A broad question that does not clearly belong to one of the "
        "specific supported business categories."
    ),
}


def _high_confidence_rule(
    question: str
):
    """
    Resolve obvious semantic cases before using the LLM.

    Returns:
        supported intent string
        or None when the question should go to semantic classification.
    """

    q = question.lower().strip()

    # --------------------------------------------------
    # SCENARIOS
    # --------------------------------------------------

    scenario_phrases = [
        "what if",
        "what happens if",
        "simulate",
        "simulation",
        "scenario",
    ]

    if any(
        phrase in q
        for phrase in scenario_phrases
    ):
        return "scenario"

    # --------------------------------------------------
    # CROSS-METRIC QUESTIONS
    # --------------------------------------------------

    revenue_terms = [
        "revenue",
        "sales",
        "income",
        "earnings",
        "turnover",
        "money",
    ]

    order_terms = [
        "orders",
        "order volume",
        "order count",
    ]

    delivery_terms = [
        "delivery",
        "deliveries",
        "delivered",
    ]

    cancellation_terms = [
        "cancellation",
        "cancellations",
        "cancelled",
        "canceled",
    ]

    dimensions = []

    if any(
        term in q
        for term in revenue_terms
    ):
        dimensions.append(
            "revenue"
        )

    if any(
        term in q
        for term in order_terms
    ):
        dimensions.append(
            "orders"
        )

    if any(
        term in q
        for term in delivery_terms
    ):
        dimensions.append(
            "delivery"
        )

    if any(
        term in q
        for term in cancellation_terms
    ):
        dimensions.append(
            "cancellation"
        )

    dimensions = list(
        dict.fromkeys(
            dimensions
        )
    )

    # Explicit comparison/linking words strongly indicate
    # a multi-metric business question.

    cross_metric_connectors = [
        "even though",
        "while",
        "despite",
        "although",
        "but",
        "whereas",
        "and delivery",
        "and cancellations",
        "and orders",
        "and revenue",
    ]

    if (
        len(dimensions) >= 2
        and any(
            connector in q
            for connector
            in cross_metric_connectors
        )
    ):
        return "general_business"

    # --------------------------------------------------
    # PRODUCT
    # --------------------------------------------------

    product_terms = [
        "product",
        "products",
        "sku",
        "skus",
        "product mix",
        "best selling",
        "best-selling",
        "top product",
        "top products",
        "units sold",
        "product revenue",
        "product contribution",
        "product concentration",
    ]

    if any(
        term in q
        for term in product_terms
    ):
        return "product"

    # --------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------

    customer_terms = [
        "customer",
        "customers",
        "repeat purchase",
        "repeat purchases",
        "retention",
        "cohort",
        "cohorts",
        "ltv",
        "cac",
        "returning customer",
        "returning customers",
        "new customer",
        "new customers",
        "customer behaviour",
        "customer behavior",
        "customer segmentation",
    ]

    if any(
        term in q
        for term in customer_terms
    ):
        return "customer"

    # --------------------------------------------------
    # LOGISTICS
    # --------------------------------------------------

    logistics_terms = [
        "delivery tat",
        "p90 delivery",
        "p90 tat",
        "late delivery",
        "late deliveries",
        "arriving late",
        "arrive late",
        "on-time delivery",
        "on time delivery",
        "promised delivery",
        "delivery promise",
        "shipping",
        "freight",
        "carrier handover",
        "carrier",
        "courier",
        "logistics",
        "rto",
        "ndr",
        "cod",
        "prepaid",
        "fulfilment tat",
        "fulfillment tat",
        "delivery sla",
    ]

    if any(
        term in q
        for term in logistics_terms
    ):
        return "logistics"

    # --------------------------------------------------
    # CANCELLATION
    # --------------------------------------------------

    if any(
        term in q
        for term in cancellation_terms
    ):
        return "cancellation"

    # --------------------------------------------------
    # SIMPLE REVENUE
    # --------------------------------------------------

    if (
        len(dimensions) == 1
        and dimensions[0] == "revenue"
    ):
        return "revenue"

    # --------------------------------------------------
    # DELIVERY PERFORMANCE
    # --------------------------------------------------

    delivery_performance_phrases = [
        "delivery rate",
        "delivery performance",
        "successful deliveries",
        "delivery success",
        "getting better at delivering",
        "deliveries improving",
        "deliveries worsening",
    ]

    if any(
        phrase in q
        for phrase
        in delivery_performance_phrases
    ):
        return "delivery"

    # --------------------------------------------------
    # SIMPLE ORDERS
    # --------------------------------------------------

    if (
        len(dimensions) == 1
        and dimensions[0] == "orders"
    ):
        return "orders"

    # --------------------------------------------------
    # MANAGEMENT / HEALTH
    # --------------------------------------------------

    business_health_phrases = [
        "what should management",
        "what should we do",
        "what should we improve",
        "what should we focus on",
        "management focus",
        "recommend",
        "recommendation",
        "recommendations",
        "business health",
        "priority",
        "priorities",
        "risk",
        "risks",
    ]

    if any(
        phrase in q
        for phrase
        in business_health_phrases
    ):
        return "business_health"

    # --------------------------------------------------
    # TRENDS
    # --------------------------------------------------

    trend_terms = [
        "trend",
        "trends",
        "pattern",
        "patterns",
        "over time",
    ]

    if any(
        term in q
        for term in trend_terms
    ):
        return "trends"

    # --------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------

    performance_phrases = [
        "which month performed",
        "best month",
        "worst month",
        "best period",
        "worst period",
        "monthly performance",
        "business performing",
        "overall performance",
    ]

    if any(
        phrase in q
        for phrase
        in performance_phrases
    ):
        return "performance"

    return None


def _keyword_fallback(
    question: str
) -> str:
    """
    Deterministic classifier used if the LLM
    is unavailable or returns an invalid result.
    """

    high_confidence = (
        _high_confidence_rule(
            question
        )
    )

    if high_confidence:
        return high_confidence

    q = question.lower().strip()

    matched_categories = []

    # --------------------------------------------------
    # BROADER FALLBACK KEYWORDS
    # --------------------------------------------------

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
        "order",
        "orders",
        "order volume",
        "order count",
        "ordering",
        "buying",
        "purchases",
    ]

    delivery_keywords = [
        "delivery",
        "deliveries",
        "delivered",
    ]

    cancellation_keywords = [
        "cancel",
        "cancelled",
        "canceled",
        "cancellation",
        "cancellations",
    ]

    product_keywords = [
        "product",
        "products",
        "sku",
        "skus",
    ]

    customer_keywords = [
        "customer",
        "customers",
        "retention",
        "repeat purchase",
        "ltv",
        "cac",
    ]

    logistics_keywords = [
        "logistics",
        "shipping",
        "freight",
        "courier",
        "rto",
        "ndr",
        "delivery tat",
        "late delivery",
    ]

    if any(
        keyword in q
        for keyword in revenue_keywords
    ):
        matched_categories.append(
            "revenue"
        )

    if any(
        keyword in q
        for keyword in order_keywords
    ):
        matched_categories.append(
            "orders"
        )

    if any(
        keyword in q
        for keyword in delivery_keywords
    ):
        matched_categories.append(
            "delivery"
        )

    if any(
        keyword in q
        for keyword in cancellation_keywords
    ):
        matched_categories.append(
            "cancellation"
        )

    if any(
        keyword in q
        for keyword in product_keywords
    ):
        matched_categories.append(
            "product"
        )

    if any(
        keyword in q
        for keyword in customer_keywords
    ):
        matched_categories.append(
            "customer"
        )

    if any(
        keyword in q
        for keyword in logistics_keywords
    ):
        matched_categories.append(
            "logistics"
        )

    matched_categories = list(
        dict.fromkeys(
            matched_categories
        )
    )

    if len(
        matched_categories
    ) > 1:
        return "general_business"

    if len(
        matched_categories
    ) == 1:
        return matched_categories[0]

    return "general"


def classify_question(
    question: str
) -> str:
    """
    Classify natural-language business questions
    into a supported ProfitLens intent.

    Flow:
    1. High-confidence deterministic rules.
    2. Semantic LLM classification.
    3. Deterministic keyword fallback.
    """

    if not isinstance(
        question,
        str
    ):
        return "general"

    question = question.strip()

    if not question:
        return "general"

    # --------------------------------------------------
    # 1. HIGH-CONFIDENCE RULES
    # --------------------------------------------------

    deterministic_intent = (
        _high_confidence_rule(
            question
        )
    )

    if deterministic_intent:
        return deterministic_intent

    # --------------------------------------------------
    # 2. LLM SEMANTIC CLASSIFICATION
    # --------------------------------------------------

    intent_descriptions = "\n".join(
        [
            f"- {intent}: {description}"
            for intent, description
            in SUPPORTED_INTENTS.items()
        ]
    )

    prompt = f"""
You are the intent classifier for ProfitLens,
an AI Business Analyst for D2C brands.

Understand the semantic meaning of the user's
complete business question.

SUPPORTED INTENTS:

{intent_descriptions}

RULES:

1. Return exactly one supported intent.

2. Do not classify based only on isolated keywords.

3. If one business dimension is clearly being asked
   about, use that specific intent.

4. If two or more separate business dimensions are
   materially compared or connected, use:

   general_business

5. Explicit what-if and simulation questions use:

   scenario

6. Product/SKU questions use:

   product

7. Customer retention, repeat purchase, cohort,
   CAC or LTV questions use:

   customer

8. Detailed fulfilment questions involving TAT,
   late delivery, promised delivery, freight,
   courier, RTO, NDR, COD/prepaid or shipping use:

   logistics

9. Simple delivery-success or delivery-rate
   questions use:

   delivery

10. Recommendations, management priorities and
    business-health questions use:

    business_health


EXAMPLES:

"Which products generated the most revenue?"
-> product

"Which SKUs sold the most units?"
-> product

"Are customers buying from us again?"
-> customer

"What is our repeat purchase rate?"
-> customer

"What is our P90 delivery TAT?"
-> logistics

"Are deliveries arriving late?"
-> logistics

"How successful are our deliveries?"
-> delivery

"What if AOV increases by 5%?"
-> scenario

"What happens if we recover half of lost orders?"
-> scenario

"Why did revenue decline?"
-> revenue

"Why are orders falling?"
-> orders

"Why did revenue decline even though delivery improved?"
-> general_business

"Why did orders fall while cancellations increased?"
-> general_business

"What should management focus on?"
-> business_health

"Which month performed best?"
-> performance

"What patterns are visible over time?"
-> trends


USER QUESTION:

{question}

Return ONLY valid JSON:

{{
    "intent": "one_supported_intent"
}}
"""

    try:

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
            timeout=5.0
        )

        output = (
            interaction
            .output_text
            .strip()
        )

        response = json.loads(
            output
        )

        intent = response.get(
            "intent"
        )

        if intent in SUPPORTED_INTENTS:
            return intent

        return _keyword_fallback(
            question
        )

    except Exception:

        return _keyword_fallback(
            question
        )
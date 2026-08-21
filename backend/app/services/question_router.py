import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv(
    "GEMINI_API_KEY"
)

client = (
    genai.Client(
        api_key=api_key
    )
    if api_key
    else None
)


# ============================================================
# SUPPORTED INTENTS
# ============================================================


SUPPORTED_INTENTS = {

    "revenue": (
        "Revenue, sales, realized revenue, AOV "
        "and revenue growth or decline."
    ),

    "profitability": (
        "Profit, profitability, gross profit, gross margin, "
        "contribution profit, contribution margin and "
        "profit after marketing."
    ),

    "orders": (
        "Order volume, number of orders and order growth."
    ),

    "marketing": (
        "Marketing spend, ROAS, CAC, campaigns, channels, "
        "attributed revenue, attributed orders, sessions, "
        "clicks and marketing efficiency."
    ),

    "product": (
        "Products, SKUs, product revenue, units sold, "
        "product mix, gross margin and product performance."
    ),

    "customer": (
        "Customers, repeat purchase, retention, cohorts, "
        "new customers, repeat customers and customer behaviour."
    ),

    "inventory": (
        "Inventory, stock, warehouses, reorder risk, "
        "overstock, slow-moving inventory and trapped capital."
    ),

    "logistics": (
        "Logistics, shipping, courier performance, RTO, "
        "NDR, COD versus prepaid, delivery TAT and zones."
    ),

    "delivery": (
        "Simple delivery success or delivery-rate questions."
    ),

    "cancellation": (
        "Cancelled orders and cancellation rates."
    ),

    "trends": (
        "Trends, patterns and changes over time."
    ),

    "performance": (
        "Overall business performance or period comparisons."
    ),

    "business_health": (
        "Business health, biggest problems, management "
        "priorities, risks, opportunities and recommendations."
    ),

    "scenario": (
        "What-if questions and simulations."
    ),

    "general_business": (
        "Questions materially combining multiple "
        "business dimensions."
    ),

    "general": (
        "Broad business questions that do not clearly "
        "belong to another supported category."
    ),
}


# ============================================================
# HIGH-CONFIDENCE RULES
# ============================================================


def _high_confidence_rule(
    question: str,
):
    q = question.lower().strip()

    # --------------------------------------------------------
    # SCENARIO
    # --------------------------------------------------------

    scenario_phrases = [
        "what if",
        "what happens if",
        "simulate",
        "simulation",
        "scenario",
        "impact if",
    ]

    if any(
        phrase in q
        for phrase in scenario_phrases
    ):
        return "scenario"

    # --------------------------------------------------------
    # BUSINESS HEALTH
    # --------------------------------------------------------

    business_health_phrases = [
        "what should management",
        "what should we do",
        "what should we improve",
        "what should we focus on",
        "what should management focus on",
        "management focus",
        "management priority",
        "management priorities",
        "business health",
        "health of the business",
        "biggest problem",
        "biggest problems",
        "three biggest problems",
        "top problems",
        "major problem",
        "major problems",
        "biggest risk",
        "biggest risks",
        "major risk",
        "major risks",
        "top risks",
        "priority",
        "priorities",
        "recommend",
        "recommendation",
        "recommendations",
        "what needs attention",
        "what requires attention",
    ]

    if any(
        phrase in q
        for phrase in business_health_phrases
    ):
        return "business_health"

    # --------------------------------------------------------
    # CROSS-METRIC DETECTION
    # --------------------------------------------------------

    dimensions = []

    dimension_terms = {

        "revenue": [
            "revenue",
            "sales",
            "aov",
            "average order value",
        ],

        "orders": [
            "orders",
            "order volume",
            "order count",
        ],

        "profitability": [
            "profit",
            "profitability",
            "margin",
            "contribution profit",
        ],

        "marketing": [
            "marketing",
            "roas",
            "cac",
            "campaign",
            "ad spend",
        ],

        "delivery": [
            "delivery",
            "deliveries",
            "delivered",
        ],

        "logistics": [
            "rto",
            "ndr",
            "courier",
            "shipping",
            "logistics",
        ],

        "inventory": [
            "inventory",
            "stock",
            "reorder",
            "overstock",
        ],

        "customer": [
            "customer",
            "customers",
            "retention",
            "repeat customer",
        ],
    }

    for (
        dimension,
        terms,
    ) in dimension_terms.items():

        if any(
            term in q
            for term in terms
        ):
            dimensions.append(
                dimension
            )

    dimensions = list(
        dict.fromkeys(
            dimensions
        )
    )

    connectors = [
        "even though",
        "while",
        "despite",
        "although",
        "but",
        "whereas",
        "versus",
        " vs ",
        "compared with",
        "compared to",
    ]

    if (
        len(dimensions) >= 2
        and any(
            connector in q
            for connector in connectors
        )
    ):
        return "general_business"

    # --------------------------------------------------------
    # INVENTORY
    # --------------------------------------------------------

    inventory_terms = [
        "inventory",
        "stock",
        "stockout",
        "stock out",
        "out of stock",
        "out-of-stock",
        "low stock",
        "reorder",
        "re-order",
        "reorder point",
        "reorder candidate",
        "reorder candidates",
        "overstock",
        "over stock",
        "excess stock",
        "slow moving",
        "slow-moving",
        "trapped inventory",
        "trapped stock",
        "inventory cost",
        "stock coverage",
        "stock to sales",
        "stock-to-sales",
        "warehouse inventory",
        "inventory risk",
    ]

    if any(
        term in q
        for term in inventory_terms
    ):
        return "inventory"

    # --------------------------------------------------------
    # PROFITABILITY
    # --------------------------------------------------------

    profitability_terms = [
        "profitability",
        "profitable",
        "profit",
        "profits",
        "gross profit",
        "gross margin",
        "contribution profit",
        "contribution margin",
        "profit after marketing",
        "margin after marketing",
        "loss making",
        "loss-making",
        "margin",
        "margins",
    ]

    if any(
        term in q
        for term in profitability_terms
    ):
        return "profitability"

    # --------------------------------------------------------
    # MARKETING
    # --------------------------------------------------------

    marketing_terms = [
        "marketing",
        "marketing spend",
        "ad spend",
        "advertising spend",
        "roas",
        "paid roas",
        "cac",
        "customer acquisition cost",
        "cost per order",
        "attributed revenue",
        "attributed orders",
        "acquisition channel",
        "campaign",
        "campaigns",
        "sessions",
        "clicks",
        "ctr",
        "conversion rate",
        "session conversion",
    ]

    if any(
        term in q
        for term in marketing_terms
    ):
        return "marketing"

    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    customer_terms = [
        "customer",
        "customers",
        "repeat purchase",
        "repeat customer",
        "repeat customers",
        "retention",
        "cohort",
        "cohorts",
        "returning customer",
        "new customer",
        "new customers",
        "active customer",
        "customer behaviour",
        "customer behavior",
        "customer segmentation",
        "orders per customer",
    ]

    if any(
        term in q
        for term in customer_terms
    ):
        return "customer"

    # --------------------------------------------------------
    # LOGISTICS
    # --------------------------------------------------------

    logistics_terms = [
        "delivery tat",
        "p90 delivery",
        "p90 tat",
        "late delivery",
        "late deliveries",
        "on-time delivery",
        "on time delivery",
        "promised delivery",
        "delivery promise",
        "shipping",
        "freight",
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
        "zone performance",
        "courier performance",
    ]

    if any(
        term in q
        for term in logistics_terms
    ):
        return "logistics"

    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

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
        "product concentration",
    ]

    if any(
        term in q
        for term in product_terms
    ):
        return "product"

    # --------------------------------------------------------
    # CANCELLATION
    # --------------------------------------------------------

    cancellation_terms = [
        "cancellation",
        "cancellations",
        "cancelled",
        "canceled",
        "cancel rate",
    ]

    if any(
        term in q
        for term in cancellation_terms
    ):
        return "cancellation"

    # --------------------------------------------------------
    # DELIVERY
    # --------------------------------------------------------

    delivery_terms = [
        "delivery rate",
        "delivery success",
        "successful deliveries",
        "delivery performance",
        "deliveries improving",
        "deliveries worsening",
    ]

    if any(
        term in q
        for term in delivery_terms
    ):
        return "delivery"

    # --------------------------------------------------------
    # TRENDS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------------

    performance_terms = [
        "which month performed",
        "best month",
        "worst month",
        "best period",
        "worst period",
        "monthly performance",
        "overall performance",
    ]

    if any(
        term in q
        for term in performance_terms
    ):
        return "performance"

    # --------------------------------------------------------
    # REVENUE
    # --------------------------------------------------------

    revenue_terms = [
        "revenue",
        "sales",
        "income",
        "earnings",
        "turnover",
        "aov",
        "average order value",
        "made less",
        "made more",
    ]

    if any(
        term in q
        for term in revenue_terms
    ):
        return "revenue"

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    order_terms = [
        "orders",
        "order volume",
        "order count",
        "ordering",
        "purchases",
    ]

    if any(
        term in q
        for term in order_terms
    ):
        return "orders"

    return None


# ============================================================
# DETERMINISTIC FALLBACK
# ============================================================


def _keyword_fallback(
    question: str,
) -> str:

    high_confidence = (
        _high_confidence_rule(
            question
        )
    )

    if high_confidence:
        return high_confidence

    q = question.lower().strip()

    keyword_groups = {

        "inventory": [
            "inventory",
            "stock",
            "warehouse",
            "reorder",
            "overstock",
        ],

        "profitability": [
            "profit",
            "margin",
            "profitable",
            "profitability",
        ],

        "marketing": [
            "marketing",
            "campaign",
            "roas",
            "cac",
            "ad spend",
        ],

        "product": [
            "product",
            "products",
            "sku",
            "skus",
        ],

        "customer": [
            "customer",
            "customers",
            "retention",
            "cohort",
        ],

        "logistics": [
            "logistics",
            "shipping",
            "courier",
            "rto",
            "ndr",
            "freight",
        ],

        "revenue": [
            "revenue",
            "sales",
            "aov",
        ],

        "orders": [
            "order",
            "orders",
        ],

        "delivery": [
            "delivery",
            "delivered",
        ],

        "cancellation": [
            "cancel",
            "cancelled",
            "cancellation",
        ],
    }

    matches = []

    for (
        intent,
        keywords,
    ) in keyword_groups.items():

        if any(
            keyword in q
            for keyword in keywords
        ):
            matches.append(
                intent
            )

    matches = list(
        dict.fromkeys(
            matches
        )
    )

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        return "general_business"

    return "general"


# ============================================================
# PUBLIC CLASSIFIER
# ============================================================


def classify_question(
    question: str,
) -> str:

    if not isinstance(
        question,
        str,
    ):
        return "general"

    question = question.strip()

    if not question:
        return "general"

    deterministic_intent = (
        _high_confidence_rule(
            question
        )
    )

    if deterministic_intent:
        return deterministic_intent

    intent_descriptions = "\n".join(
        [
            f"- {intent}: {description}"
            for (
                intent,
                description,
            )
            in SUPPORTED_INTENTS.items()
        ]
    )

    prompt = f"""
You are the intent classifier for ProfitLens,
an AI Business Analyst for D2C brands.

Classify the user's complete business question.

SUPPORTED INTENTS:

{intent_descriptions}

ROUTING RULES:

1. Return exactly one supported intent.

2. Profit and margin questions use profitability.

3. Marketing spend, ROAS, CAC and campaign
   questions use marketing.

4. Inventory, stock, reorder and overstock
   questions use inventory.

5. Product commercial performance uses product.

6. Repeat customers, cohorts and retention
   use customer.

7. RTO, NDR, couriers, COD/prepaid and TAT
   use logistics.

8. Simple delivery-success questions use delivery.

9. Revenue and AOV questions use revenue.

10. Order-volume questions use orders.

11. Explicit what-if questions use scenario.

12. Questions about biggest problems, biggest risks,
    management priorities or what the business should
    do next use business_health.

13. Questions materially combining multiple business
    dimensions use general_business.


EXAMPLES:

"Why did revenue decline?"
-> revenue

"Why did revenue decline even though delivery improved?"
-> general_business

"Are we profitable after marketing?"
-> profitability

"What is our contribution margin?"
-> profitability

"Is our marketing efficient?"
-> marketing

"What is our ROAS?"
-> marketing

"Which products generated the most revenue?"
-> product

"What is our repeat customer rate?"
-> customer

"Why is RTO high?"
-> logistics

"Which courier should we be concerned about?"
-> logistics

"Which inventory problems require immediate action?"
-> inventory

"Which SKUs need reordering?"
-> inventory

"What are the three biggest problems in the business?"
-> business_health

"What should management focus on next?"
-> business_health


USER QUESTION:

{question}


Return ONLY valid JSON:

{{
    "intent": "one_supported_intent"
}}
"""

    if client is None:
        return _keyword_fallback(
            question
        )

    try:

        interaction = (
            client.interactions.create(
                model="gemini-3.6-flash",
                input=prompt,
                timeout=5.0,
            )
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

    except Exception:
        pass

    return _keyword_fallback(
        question
    )
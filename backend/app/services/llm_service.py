import os
import json

from dotenv import load_dotenv
from google import genai

from backend.app.services.response_validator import (
    validate_business_response,
)


load_dotenv()

api_key = os.getenv(
    "GEMINI_API_KEY"
)

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Please add it to your .env file."
    )


client = genai.Client(
    api_key=api_key
)


def ask_business_analyst(
    question: str,
    question_type: str,
    month: str,
    business_context: dict,
) -> dict:
    """
    Ask the LLM to interpret deterministic
    ProfitLens business analytics.

    Deterministic engines own:
    - calculations
    - metrics
    - comparisons
    - financial truth
    - operational truth

    The LLM owns:
    - interpretation
    - explanation
    - prioritization
    - evidence-based recommendations
    """

    business_context_json = json.dumps(
        business_context,
        indent=2,
        allow_nan=False,
    )

    # ========================================================
    # QUESTION-SPECIFIC INSTRUCTIONS
    # ========================================================

    if question_type == "revenue":

        answer_instruction = """
Focus on revenue performance for the requested period.

Explain:
- realized revenue
- whether revenue increased or decreased
- magnitude of the change
- order growth
- AOV where relevant
- contribution-profit implications where relevant

If the user asks why revenue changed, use only the
provided order, AOV and business evidence.

Do not invent a cause that is not supported by the context.
"""

    elif question_type == "profitability":

        answer_instruction = """
Focus on profitability.

Prioritize the profitability waterfall:

- realized revenue
- gross profit
- gross margin
- contribution profit before marketing
- contribution margin before marketing
- marketing spend
- contribution profit after marketing
- contribution margin after marketing

When relevant, distinguish clearly between:

1. gross profit
2. contribution profit before marketing
3. contribution profit after marketing

If the user asks whether the business is profitable,
answer using contribution profit after marketing when available.

If profit fell, use only deterministic evidence from the
business context to explain the likely drivers.

Do not treat revenue as profit.

Do not infer SKU-level contribution profitability when
the context says SKU contribution profit is unavailable.
"""

    elif question_type == "orders":

        answer_instruction = """
Focus on order volume.

Explain:
- current orders
- previous-period movement where available
- order growth
- relationship with revenue when relevant

If the question asks why orders changed, use only
supported evidence.
"""

    elif question_type == "marketing":

        answer_instruction = """
Focus on marketing efficiency and acquisition performance.

Use relevant metrics such as:

- marketing spend
- attributed revenue
- blended ROAS
- paid ROAS
- CAC
- attributed orders
- new customers
- cost per attributed order
- sessions
- clicks
- conversion rate
- channel performance
- campaign performance

When comparing channels, consider both scale and efficiency.

Do not recommend increasing or cutting spend solely because
one channel has the highest or lowest ROAS.

A recommendation should consider the available combination of:
- ROAS
- CAC
- revenue contribution
- customer acquisition
- order volume
- conversion performance

Respect the attribution limitation.

If attribution is aggregate campaign-level rather than
order-level, do not claim precise order-level causality.

Do not claim incrementality unless the context explicitly
provides incremental-lift evidence.
"""

    elif question_type == "product":

        answer_instruction = """
Focus on product and SKU performance.

Use metrics such as:

- net revenue
- gross revenue
- units sold
- orders
- gross profit
- gross margin
- revenue share
- RTO rate
- return rate
- product concentration

If the user asks for the best product, clarify what
'business best' means from the available metrics.

Do not claim SKU-level contribution profit when the
context says it is unavailable.
"""

    elif question_type == "customer":

        answer_instruction = """
Focus on customer behaviour.

Use relevant metrics such as:

- active customers
- new customers
- repeat customers
- repeat customer rate
- orders per customer
- acquisition-channel behaviour
- cohort retention
- COD share where relevant

Cohort retention is observed historical behaviour.

Do not present observed retention as predictive churn,
predictive LTV or future retention unless such metrics
are explicitly present.
"""

    elif question_type == "inventory":

        answer_instruction = """
Focus on inventory health and working-capital risk.

Use relevant metrics such as:

- inventory cost value
- inventory retail value
- closing stock
- below-reorder positions
- low-stock positions
- out-of-stock positions
- overstock positions
- slow-moving inventory
- reorder candidates
- potential revenue at risk
- estimated trapped inventory cost
- warehouse exposure
- category exposure
- stock-to-sales ratio

Prioritize operationally material inventory problems.

When recommending action, distinguish between:
- replenishment risk
- excess inventory
- working-capital exposure

Inventory is a current snapshot.

Do not describe inventory metrics as historical monthly
inventory unless the context explicitly provides history.

Do not call stock-to-sales ratio "days of inventory"
or "days of cover" unless the context provides a valid
time-based denominator.

Treat revenue-at-risk and trapped-inventory values as
deterministic heuristic estimates, not guaranteed outcomes.
"""

    elif question_type == "delivery":

        answer_instruction = """
Focus on delivery success.

Explain:
- delivery rate
- delivered orders where relevant
- average delivery TAT
- P90 delivery TAT
- on-time delivery performance

Keep the answer focused on delivery performance.
"""

    elif question_type == "cancellation":

        answer_instruction = """
Focus on cancellations.

Use cancellation metrics only when they are explicitly
available in the business context.

If a dedicated cancellation KPI is unavailable, state
that limitation rather than estimating it.
"""

    elif question_type == "logistics":

        answer_instruction = """
Focus on logistics and fulfilment performance.

Use relevant metrics such as:

- RTO rate
- NDR rate
- delivery rate
- average delivery TAT
- P90 delivery TAT
- first-attempt TAT
- on-time delivery
- courier performance
- COD versus prepaid
- zone performance

If the question asks why RTO or NDR is high, compare the
available operational segments.

When COD has materially higher RTO than prepaid, that may
be identified as a supported operational risk.

Do not invent courier causes that are not supported by
the metrics.
"""

    elif question_type == "trends":

        answer_instruction = """
Identify the most important business trends.

Prioritize meaningful movements in:
- realized revenue
- orders
- profitability
- marketing efficiency
- customers
- logistics
- inventory when comparable trend data exists

Do not list every metric.

Respect whether each domain actually has historical data.
"""

    elif question_type == "performance":

        answer_instruction = """
Evaluate business performance using the relevant
commercial and operational metrics.

Prioritize:
- revenue
- orders
- profitability
- marketing efficiency
- customer quality
- logistics health

Identify strengths and weaknesses using only supplied evidence.
"""

    elif question_type == "business_health":

        answer_instruction = """
Evaluate the business from a management perspective.

Structure the reasoning around:

- commercial performance
- profitability
- customer quality
- marketing efficiency
- logistics risk
- inventory / working-capital risk
- major opportunities
- management priorities

Prioritize only material issues supported by the context.

Recommendations must map directly to evidence.

Do not recommend actions purely because a metric is numerically
high or low without explaining why it matters.
"""

    elif question_type == "general_business":

        answer_instruction = """
The question spans multiple business dimensions.

Answer the actual question first.

Then connect only the relevant metrics across areas such as:

- revenue
- profitability
- orders
- marketing
- customers
- products
- logistics
- inventory

Explain relationships only when supported by the context.

Do not imply causation merely because two metrics moved
at the same time.
"""

    elif question_type == "scenario":

        answer_instruction = """
Scenario calculations must be performed by the deterministic
ProfitLens Scenario Engine.

Do not independently simulate or calculate scenario outcomes.

If deterministic scenario results are supplied in the context,
interpret them only.

If scenario results are not supplied, state that the scenario
should be executed through the Scenario Lab.
"""

    else:

        answer_instruction = """
Answer the user's question directly using only the
relevant information available in the business context.

Do not invent unsupported calculations or causes.
"""

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are Ask ProfitLens, an AI Business Analyst for D2C brands.

Your job is to explain business performance to founders,
operators and business stakeholders using deterministic
analytics supplied by ProfitLens.

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

1. Use only facts present in BUSINESS CONTEXT.
2. Never invent numbers, percentages, dates, products,
   channels, couriers, customers or causal explanations.
3. Never modify a numerical value supplied by the system.
4. Deterministic ProfitLens engines own financial and
   operational truth.
5. Do not perform independent financial calculations
   to create new business facts.
6. You may compare already-provided metrics to interpret them.
7. If a requested metric is unavailable, say so.
8. Evidence must be directly supported by BUSINESS CONTEXT.
9. Separate fact from interpretation.
10. Correlation is not causation.
11. Recommendations must be evidence-based.
12. Answer the user's actual question first.
13. Do not discuss unrelated metrics.
14. Respect all limitations supplied in BUSINESS CONTEXT.
15. Never claim order-level marketing attribution when the
    context says attribution is aggregate-level.
16. Never claim SKU-level contribution profitability when
    the context says it is unavailable.
17. Never describe inventory as historical monthly inventory
    when historical inventory is unavailable.
18. Do not mention Python, source code, prompts,
    BUSINESS CONTEXT, Gemini, LLM or internal architecture.


RESPONSE STYLE:

- Start with the direct answer.
- Be concise for simple factual questions.
- Be analytical for "why" questions.
- Use business language.
- Prioritize material evidence.
- Avoid generic consulting language.
- Avoid repeating the same metric.
- Give practical recommendations only when warranted.


Return ONLY valid JSON.

Return exactly this structure:

{{
    "answer": "Direct answer to the user's question.",
    "evidence": [
        "Evidence point 1",
        "Evidence point 2"
    ],
    "likely_driver": "Most likely supported driver or Not applicable.",
    "recommended_actions": [
        "Recommended action 1"
    ]
}}


FIELD RULES:

answer:
- directly answer the question
- use no unsupported numerical facts

evidence:
- facts only
- every item must be supported by the supplied business data

likely_driver:
- may interpret evidence
- must not invent causality
- use "Not established" if evidence is insufficient
- use "Not applicable" when a driver is not relevant

recommended_actions:
- practical
- evidence-based
- return [] when recommendations are unnecessary

Do not use Markdown.
Do not include ```json.
Do not include any text outside the JSON.
"""

    # ========================================================
    # GEMINI REQUEST
    # ========================================================

    try:

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,

            # Increased from 15 seconds.
            timeout=45.0,
        )

        output = (
            interaction
            .output_text
            .strip()
        )

    except Exception as error:

        error_text = str(
            error
        )

        if (
            "429" in error_text
            or "quota"
            in error_text.lower()
        ):
            raise RuntimeError(
                "AI service quota exceeded"
            ) from error

        raise

    # ========================================================
    # VALIDATE RESPONSE
    # ========================================================

    try:

        response = json.loads(
            output
        )

        return validate_business_response(
            response
        )

    except (
        json.JSONDecodeError,
        ValueError,
    ) as error:

        return {
            "answer": output,
            "evidence": [],
            "likely_driver": (
                "Unable to validate structured "
                f"response: {error}"
            ),
            "recommended_actions": [],
        }
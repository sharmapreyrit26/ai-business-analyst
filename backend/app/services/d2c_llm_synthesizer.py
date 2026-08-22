from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from google import genai

from backend.app.services.d2c_synthesis_validator import (
    validate_d2c_synthesis_response,
)


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


def synthesize_d2c_response(
    *,
    synthesis_context: dict,
):
    """
    Convert governed ProfitLens analysis into an executive
    natural-language answer.

    The model does NOT own:
    - financial truth
    - operational truth
    - evidence truth
    - causal truth
    - recommendation truth

    It only synthesizes the supplied governed analysis.
    """

    if client is None:

        raise RuntimeError(
            "AI service unavailable"
        )


    context_json = json.dumps(
        synthesis_context,
        indent=2,
        allow_nan=False,
    )


    prompt = f"""
You are Ask ProfitLens, an executive business-analysis
communication layer for D2C brands.

Your job is to synthesize GOVERNED ANALYSIS into a concise,
accurate executive answer.

You are NOT responsible for discovering new facts,
calculating metrics or inventing actions.


GOVERNED ANALYSIS:

{context_json}


STRICT RULES:

1. Use only information in GOVERNED ANALYSIS.

2. Do not invent or calculate new numbers.

3. verified_facts are authoritative measured facts.

4. supported_inferences may be described only as signals,
   associations or interpretations.

5. Never present a supported inference as causal proof.

6. unresolved_hypotheses are possible explanations only.
   Never present them as established causes.

7. If material hypotheses remain unresolved, explicitly
   communicate that the underlying cause is not fully proven
   when relevant to the user's question.

8. Management actions may come ONLY from approved_actions.

9. Never recommend anything from blocked_actions.

10. Do not invent a management recommendation that is not
    present in approved_actions.

11. Respect the readiness of every approved action:
    - act_now means operationally actionable now.
    - test_first means use a limited measured test.
    - investigate_first means gather evidence first.

12. Keep the answer focused on the user's actual question.

13. Prefer material findings over listing every available metric.

14. Do not mention internal architecture, code, prompts,
    Python, LLMs, Gemini, synthesis context or internal engines.

15. Do not use Markdown.


STYLE:

- Lead with the direct answer.
- Write like a strong business analyst speaking to a founder.
- Separate measured result from interpretation naturally.
- State uncertainty explicitly where necessary.
- Keep simple questions concise.
- For "why" or business-health questions, provide enough
  reasoning to explain what is known and what remains unproven.


Return ONLY valid JSON with this exact structure:

{{
    "answer": "Executive synthesis.",
    "used_claim_ids": [
        "claim_id"
    ],
    "used_hypothesis_ids": [
        "hypothesis_id"
    ],
    "used_action_ids": [
        "recommendation_id"
    ]
}}


ID RULES:

used_claim_ids:
- include only claim IDs materially used in the answer

used_hypothesis_ids:
- include only unresolved hypotheses explicitly discussed
- return [] if none are discussed

used_action_ids:
- include only approved actions explicitly discussed
- never include blocked actions

Do not include any other fields.
Do not use ```json.
Do not include any text outside the JSON.
"""


    try:

        interaction = (
            client.interactions.create(
                model=
                    "gemini-3.6-flash",

                input=
                    prompt,

                timeout=
                    45.0,
            )
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
            "429"
            in error_text
            or "quota"
            in error_text.lower()
        ):

            raise RuntimeError(
                "AI service quota exceeded"
            ) from error

        raise


    try:

        response = json.loads(
            output
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "AI synthesis returned invalid JSON."
        ) from error


    return validate_d2c_synthesis_response(
        response,
        synthesis_context=
            synthesis_context,
    )

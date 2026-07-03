"""
Thin wrapper around the Anthropic Messages API used specifically to
generate compatibility scores. Kept isolated so it can be swapped for
another provider (OpenAI, etc.) without touching business logic.
"""
import json
import logging
from typing import Optional

import anthropic

from app.core.config import settings
from app.schemas.compatibility import LLMCompatibilityResult

logger = logging.getLogger(__name__)

_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=settings.LLM_TIMEOUT_SECONDS)
    return _client


COMPATIBILITY_PROMPT_TEMPLATE = """You are a compatibility scoring engine for a room rental platform.

Given this room listing:
{listing_json}

And this tenant profile:
{tenant_json}

Compute a compatibility score from 0 to 100 based on budget match and location match
(consider partial location matches, e.g. same city/area, as moderately compatible).
Weigh budget fit and location fit roughly equally unless one is a hard mismatch.

Return ONLY valid JSON in this exact shape, with no markdown fences and no extra text:
{{"score": <number 0-100>, "explanation": "<one or two sentence explanation>"}}
"""


def build_prompt(listing_dict: dict, tenant_dict: dict) -> str:
    return COMPATIBILITY_PROMPT_TEMPLATE.format(
        listing_json=json.dumps(listing_dict, default=str),
        tenant_json=json.dumps(tenant_dict, default=str),
    )


def get_llm_compatibility_score(listing_dict: dict, tenant_dict: dict) -> LLMCompatibilityResult:
    """
    Calls the LLM to compute a compatibility score.
    Raises an exception on any failure (timeout, bad JSON, API error) —
    caller (compatibility_service) is responsible for catching this and
    falling back to the rule-based scorer.
    """
    prompt = build_prompt(listing_dict, tenant_dict)
    client = _get_client()

    response = client.messages.create(
        model=settings.LLM_MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    text = "".join(block.text for block in response.content if block.type == "text").strip()

    # Strip accidental markdown fences if the model adds them
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    parsed = json.loads(text)
    result = LLMCompatibilityResult(score=float(parsed["score"]), explanation=str(parsed["explanation"]))

    # Clamp defensively in case the model returns out-of-range values
    result.score = max(0.0, min(100.0, result.score))
    return result

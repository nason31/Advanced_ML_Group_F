import re


# Action phrases per recommendation type.
# Covers ~80% of how Claude phrases retail actions in practice.
MARKDOWN_PHRASES = [
    "markdown", "discount", "reduce price", "price cut", "price reduction",
    "mark down", "clearance", "promotional price", "lower the price",
    "reduce retail", "cut price", "sale price", "price drop", "slash",
    "reduce margin", "offload", "liquidate", "destock",
]

RESTOCK_PHRASES = [
    "restock", "replenish", "order more", "increase stock", "increase inventory",
    "top up", "refill", "raise stock", "stock up", "place an order",
    "inventory replenishment", "purchase order", "increase supply",
    "avoid stockout", "prevent stockout", "fill the shelf",
]

PROMOTE_PHRASES = [
    "promote", "promotion", "end-cap", "end cap", "flyer", "bogo",
    "feature", "advertise", "marketing push", "highlight", "showcase",
    "weekly ad", "in-store display", "front of store", "drive awareness",
    "campaign", "boost visibility", "amplify", "capitalize",
]


def _detect_intent(text: str) -> str | None:
    """Return the dominant recommendation intent found in text, or None."""
    lower = text.lower()
    scores = {
        "markdown": sum(1 for p in MARKDOWN_PHRASES if p in lower),
        "restock": sum(1 for p in RESTOCK_PHRASES if p in lower),
        "promote": sum(1 for p in PROMOTE_PHRASES if p in lower),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def _extract_first_pct(text: str) -> float | None:
    """Extract the first percentage value (signed or unsigned) from text."""
    match = re.search(r"([+-]?\d+(?:\.\d+)?)\s*%", text)
    if match:
        return float(match.group(1))
    return None


def check(recommendation: dict, forecast_data: dict) -> dict:
    """Cross-check LLM recommendation against forecast data.

    Runs two checks:
    1. Intent check - does Claude's recommended action contradict the forecast direction?
    2. Numeric check - does the first percentage Claude cites match the actual delta_pct?

    Returns a dict with:
      flagged: bool
      reason: str          - human-readable explanation if flagged
      intent_check: str    - PASS / FLAGGED / SKIP (no intent detected)
      numeric_check: str   - PASS / FLAGGED / SKIP (no percentage found)
    """
    rec_text = recommendation.get("text", "")
    direction = forecast_data.get("direction", "")
    actual_delta = forecast_data.get("delta_pct")  # float, e.g. +419.6

    flagged = False
    reasons = []
    intent_result = "SKIP"
    numeric_result = "SKIP"

    # --- Check 1: intent vs direction ---
    intent = _detect_intent(rec_text)
    if intent:
        contradiction = (
            (intent == "markdown" and direction == "up") or
            (intent == "restock" and direction == "down") or
            (intent == "promote" and direction == "down")
        )
        if contradiction:
            flagged = True
            intent_result = "FLAGGED"
            reasons.append(
                f"Intent '{intent}' contradicts forecast direction '{direction}'."
            )
        else:
            intent_result = f"PASS - {intent} aligns with {direction} trend"

    # --- Check 2: numeric plausibility ---
    if actual_delta is not None:
        cited_pct = _extract_first_pct(rec_text)
        if cited_pct is not None:
            # Allow 2x tolerance - catches fabricated numbers, not rounding
            ratio = abs(cited_pct) / max(abs(actual_delta), 0.1)
            if ratio > 2.0 or ratio < 0.5:
                flagged = True
                numeric_result = "FLAGGED"
                reasons.append(
                    f"Cited {cited_pct:+.1f}% but data shows {actual_delta:+.1f}% - possible hallucination."
                )
            else:
                numeric_result = f"PASS - cited {cited_pct:+.1f}%, data {actual_delta:+.1f}%"

    return {
        "flagged": flagged,
        "reason": " | ".join(reasons) if reasons else "",
        "intent_check": intent_result,
        "numeric_check": numeric_result,
    }

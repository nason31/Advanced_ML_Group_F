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
    "feature placement", "feature in flyer", "advertise", "marketing push",
    "highlight", "showcase", "weekly ad", "in-store display", "front of store",
    "drive awareness", "campaign", "boost visibility", "amplify", "capitalize",
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


def _actual_delta_cited(text: str, actual_delta: float, rel_tol: float = 0.10) -> bool:
    """Return True if actual_delta appears anywhere in text within rel_tol relative tolerance.

    Scans every percentage in the text regardless of order. A citation is valid
    if abs(cited - actual) / actual <= rel_tol (10% relative). This handles
    rounding (e.g. +47% for +47.2%) and is immune to the order Claude chooses
    to mention numbers - RAG context percentages (+15% threshold, +19% YoY)
    are typically far from the SKU-level delta and will not satisfy the check.
    """
    a = abs(actual_delta)
    if a < 1.0:
        return True  # delta too small to check meaningfully
    for m in re.finditer(r"([+-]?\d+(?:\.\d+)?)\s*%", text):
        v = abs(float(m.group(1)))
        if abs(v - a) / a <= rel_tol:
            return True
    return False


def check(recommendation: dict, forecast_data: dict) -> dict:
    """Cross-check LLM recommendation against forecast data.

    Runs two checks:
    1. Intent check - does Claude's recommended action contradict the forecast direction?
    2. Numeric check - does the actual delta_pct appear anywhere in the recommendation text?

    Returns a dict with:
      flagged: bool
      reason: str          - human-readable explanation if flagged
      intent_check: str    - PASS / FLAGGED / SKIP (no intent detected)
      numeric_check: str   - PASS / FLAGGED / SKIP (delta too small to check)
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

    # --- Check 2: is the actual delta cited anywhere in the text? ---
    if actual_delta is not None and abs(actual_delta) >= 1.0:
        if _actual_delta_cited(rec_text, actual_delta):
            numeric_result = f"PASS - {actual_delta:+.1f}% found in text"
        else:
            flagged = True
            numeric_result = "FLAGGED"
            reasons.append(
                f"Forecast delta {actual_delta:+.1f}% not cited in recommendation - possible hallucination."
            )

    return {
        "flagged": flagged,
        "reason": " | ".join(reasons) if reasons else "",
        "intent_check": intent_result,
        "numeric_check": numeric_result,
    }

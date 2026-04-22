def check(recommendation: dict, forecast_data: dict) -> dict:
    """Cross-check recommendation direction against forecast data.

    Returns dict with 'flagged' bool and 'reason' string.
    Catches cases like recommending markdown when sales are trending up.
    """
    flagged = False
    reason = ""
    rec_text = recommendation.get("text", "").lower()
    direction = forecast_data.get("direction", "")

    if "markdown" in rec_text and direction == "up":
        flagged = True
        reason = "Markdown recommended but forecast direction is UP — verify intent."
    elif "restock" in rec_text and direction == "down":
        flagged = True
        reason = "Restock recommended but forecast direction is DOWN — verify stock levels."

    return {"flagged": flagged, "reason": reason}

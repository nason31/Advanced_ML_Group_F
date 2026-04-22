SYSTEM_PROMPT = """You are MerchAI, a merchandising copilot for retail store managers.
You receive sales forecast summaries and historical campaign context.
Always cite the specific data points that inform each recommendation.
Never invent figures that are not present in the data provided."""


def build_user_prompt(forecast_summary: str, context_docs: list[str]) -> str:
    context = "\n\n".join(f"- {doc}" for doc in context_docs)
    return (
        f"## Forecast Summary\n{forecast_summary}\n\n"
        f"## Historical Context\n{context}\n\n"
        "Provide 1-3 actionable recommendations (markdown, restock, or promote). "
        "For each, state the evidence."
    )
